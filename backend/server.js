const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = 5001;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Database configuration
const dbConfig = {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 3307,
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || 'rootpassword',
    database: process.env.DB_NAME || 'serverless_db'
};

const EXECUTION_ENGINE_URL = process.env.EXECUTION_ENGINE_URL || 'http://localhost:4001';

// Database connection
let connection;

// Add this retry logic to your database initialization
async function initDatabase() {
    const maxRetries = 10;
    let retries = 0;
    
    while (retries < maxRetries) {
        try {
            connection = await mysql.createConnection(dbConfig);
            console.log('✅ Connected to MySQL database');
            return;
        } catch (error) {
            retries++;
            console.log(`❌ Database connection attempt ${retries}/${maxRetries} failed:`, error.message);
            
            if (retries >= maxRetries) {
                console.error('💥 Max database connection retries reached. Exiting...');
                process.exit(1);
            }
            
            console.log(`⏳ Retrying database connection in 5 seconds...`);
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
    }
}


// CRUD Operations for Functions

// Get all functions
app.get('/api/functions', async (req, res) => {
    try {
        const [rows] = await connection.execute('SELECT * FROM functions ORDER BY created_at DESC');
        res.json(rows);
    } catch (error) {
        console.error('Error fetching functions:', error);
        res.status(500).json({ error: 'Failed to fetch functions' });
    }
});

// Get function by ID
app.get('/api/functions/:id', async (req, res) => {
    try {
        const [rows] = await connection.execute('SELECT * FROM functions WHERE id = ?', [req.params.id]);
        if (rows.length === 0) {
            return res.status(404).json({ error: 'Function not found' });
        }
        res.json(rows[0]);
    } catch (error) {
        console.error('Error fetching function:', error);
        res.status(500).json({ error: 'Failed to fetch function' });
    }
});

// Create new function
app.post('/api/functions', async (req, res) => {
    const { name, route, language, timeout_ms, code } = req.body;
    
    try {
        const [result] = await connection.execute(
            'INSERT INTO functions (name, route, language, timeout_ms, code) VALUES (?, ?, ?, ?, ?)',
            [name, route, language, timeout_ms, code]
        );
        
        const [newFunction] = await connection.execute('SELECT * FROM functions WHERE id = ?', [result.insertId]);
        res.status(201).json(newFunction[0]);
    } catch (error) {
        console.error('Error creating function:', error);
        if (error.code === 'ER_DUP_ENTRY') {
            res.status(400).json({ error: 'Function name or route already exists' });
        } else {
            res.status(500).json({ error: 'Failed to create function' });
        }
    }
});

// Update function
app.put('/api/functions/:id', async (req, res) => {
    const { name, route, language, timeout_ms, code } = req.body;
    
    try {
        const [result] = await connection.execute(
            'UPDATE functions SET name = ?, route = ?, language = ?, timeout_ms = ?, code = ? WHERE id = ?',
            [name, route, language, timeout_ms, code, req.params.id]
        );
        
        if (result.affectedRows === 0) {
            return res.status(404).json({ error: 'Function not found' });
        }
        
        const [updatedFunction] = await connection.execute('SELECT * FROM functions WHERE id = ?', [req.params.id]);
        res.json(updatedFunction[0]);
    } catch (error) {
        console.error('Error updating function:', error);
        res.status(500).json({ error: 'Failed to update function' });
    }
});

// Delete function
app.delete('/api/functions/:id', async (req, res) => {
    try {
        const [result] = await connection.execute('DELETE FROM functions WHERE id = ?', [req.params.id]);
        
        if (result.affectedRows === 0) {
            return res.status(404).json({ error: 'Function not found' });
        }
        
        res.json({ message: 'Function deleted successfully' });
    } catch (error) {
        console.error('Error deleting function:', error);
        res.status(500).json({ error: 'Failed to delete function' });
    }
});

// Execute function
app.post('/api/functions/:id/execute', async (req, res) => {
    const { executors = ['docker', 'gvisor'] } = req.body;
    
    try {
        const [functions] = await connection.execute('SELECT * FROM functions WHERE id = ?', [req.params.id]);
        
        if (functions.length === 0) {
            return res.status(404).json({ error: 'Function not found' });
        }
        
        const func = functions[0];
        const results = {};
        
        for (const executor of executors) {
            try {
                const response = await axios.post(`${EXECUTION_ENGINE_URL}/execute`, {
                    function_id: func.id,
                    code: func.code,
                    language: func.language,
                    timeout_ms: func.timeout_ms,
                    executor: executor
                });
                
                results[executor] = response.data;
                
                // Store metrics in database
                await connection.execute(
                    'INSERT INTO execution_metrics (function_id, executor_type, execution_time_ms, memory_usage_mb, cpu_usage_percent, status, error_message) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    [
                        func.id,
                        executor,
                        response.data.execution_time_ms,
                        response.data.memory_usage_mb,
                        response.data.cpu_usage_percent,
                        response.data.status,
                        response.data.error_message || null
                    ]
                );
                
            } catch (error) {
                console.error(`Error executing with ${executor}:`, error);
                results[executor] = {
                    status: 'error',
                    error_message: error.message,
                    execution_time_ms: 0,
                    memory_usage_mb: 0,
                    cpu_usage_percent: 0
                };
            }
        }
        
        res.json(results);
    } catch (error) {
        console.error('Error executing function:', error);
        res.status(500).json({ error: 'Failed to execute function' });
    }
});

// Get execution metrics
app.get('/api/functions/:id/metrics', async (req, res) => {
    try {
        const [rows] = await connection.execute(
            'SELECT * FROM execution_metrics WHERE function_id = ? ORDER BY executed_at DESC LIMIT 50',
            [req.params.id]
        );
        res.json(rows);
    } catch (error) {
        console.error('Error fetching metrics:', error);
        res.status(500).json({ error: 'Failed to fetch metrics' });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
async function startServer() {
    await initDatabase();
    app.listen(PORT, () => {
        console.log(`Backend server running on port ${PORT}`);
    });
}

startServer().catch(console.error);
