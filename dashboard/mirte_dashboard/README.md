## Set up MIRTE Dashboard

A React-based dashboard for monitoring and controlling the MIRTE robot in a ROS2 + Gazebo simulation.

### Install dashboard dependencies

Go to dashboard folder:

```bash
cd mirte_dashboard
```

Install required packages:
```bash
npm install
```

### Running the Dashboard

1. Start the MIRTE simulation in Gazebo
2. In a seperate terminal: Start rosbridge
```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```
3. In a seperate terminal: Start the React dashboard
```bash
cd mirte_dashboard
npm run dev -- --host
```

### Opening the Dashboard

1. In your laptop/desktop browser
```text
http://localhost:5173
```

---

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
