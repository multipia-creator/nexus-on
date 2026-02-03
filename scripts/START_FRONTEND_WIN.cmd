\
@echo off
cd /d %~dp0..\frontend
if not exist node_modules (
  npm i
)
if not exist .env.local (
  copy .env.local.example .env.local
)
npm run dev
