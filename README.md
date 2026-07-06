## To get react initialized

go to terminal
 
npm create vite@latest frontend -- --template react

cd frontend

npm install

npm install chart.js react-chartjs-2

npm install -D tailwindcss postcss autoprefixer

I used Pycharm, which I find that packages are significantly easier to install on.

---

# MLB Performance Prediction

## Project Overview

This project is an MLB player performance prediction web application. The goal is to help users view simple predictions for MLB players using baseball statistics.

The app will focus on predictions such as hit chance, home run chance, strikeout chance, confidence score, and risk level. The goal is to make MLB stats easier to understand by showing clear predictions and simple dashboard visuals.

## Current Tech Stack

- Frontend: React, Vite, Tailwind CSS, Chart.js
- Backend: Python, FastAPI
- Database: PostgreSQL / Supabase
- Data Source: MLB-StatsAPI
- Version Control: GitHub


## Planned Features

- Player search
- Hit chance prediction
- Home run chance prediction
- Strikeout prediction
- Win prediction
- Confidence score
- Risk level
- Simple charts for recent player trends
- Dashboard view for prediction results

## Backend Setup

The backend will use Python and FastAPI. The backend will collect MLB data, store it in the database, and send prediction results to the frontend.

More setup instructions will be added as the backend is developed.

## Database

The project is planned to use PostgreSQL. The current backend uses Supabase, which is a hosted PostgreSQL database service.

The database will store MLB teams, players, matchups, stats, and prediction results.

## Data Flow

The basic project flow is:

```text
MLB-StatsAPI → clean/filter data → PostgreSQL/Supabase → prediction model → FastAPI → React dashboard