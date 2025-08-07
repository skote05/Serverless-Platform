CREATE DATABASE IF NOT EXISTS serverless_db;
USE serverless_db;

CREATE TABLE IF NOT EXISTS functions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    route VARCHAR(255) NOT NULL UNIQUE,
    language ENUM('python', 'javascript') NOT NULL,
    timeout_ms INT NOT NULL DEFAULT 30000,
    code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS execution_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    function_id INT NOT NULL,
    executor_type ENUM('docker', 'gvisor') NOT NULL,
    execution_time_ms FLOAT NOT NULL,
    memory_usage_mb FLOAT NOT NULL,
    cpu_usage_percent FLOAT NOT NULL,
    status ENUM('success', 'error', 'timeout') NOT NULL,
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (function_id) REFERENCES functions(id) ON DELETE CASCADE
);
