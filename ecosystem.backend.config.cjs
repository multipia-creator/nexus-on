module.exports = {
  apps: [
    {
      name: 'nexus-backend',
      script: 'python3',
      args: '-m uvicorn nexus_supervisor.app:app --host 0.0.0.0 --port 8000',
      cwd: './backend',
      env: {
        PYTHONPATH: '/home/user/webapp/backend',
        PYTHON_ENV: 'production'
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: './backend/logs/error.log',
      out_file: './backend/logs/output.log',
      time: true
    }
  ]
}
