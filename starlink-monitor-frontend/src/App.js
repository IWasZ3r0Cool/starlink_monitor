import React, { useEffect, useState } from 'react';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

// Use environment variable for API base URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8080";

const App = () => {
  const [pings, setPings] = useState([]);
  const [speedTests, setSpeedTests] = useState([]);

  useEffect(() => {
    // Fetch Ping Data
    fetch(`${API_BASE_URL}/api/pings`)
      .then((res) => res.json())
      .then((data) => setPings(data));

    // Fetch Speed Test Data
    fetch(`${API_BASE_URL}/api/speedtests`)
      .then((res) => res.json())
      .then((data) => setSpeedTests(data));
  }, []);

  return (
    <div>
      <h1>Starlink Monitor</h1>

      <h2>Ping Results</h2>
      <LineChart width={600} height={300} data={pings.map(([id, timestamp, target, success]) => ({ timestamp, success }))}>
        <Line type="monotone" dataKey="success" stroke="#8884d8" />
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
      </LineChart>

      <h2>Speed Test Results</h2>
      <LineChart width={600} height={300} data={speedTests.map(([id, timestamp, download, upload, ping]) => ({ timestamp, download, upload, ping }))}>
        <Line type="monotone" dataKey="download" stroke="#82ca9d" />
        <Line type="monotone" dataKey="upload" stroke="#8884d8" />
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
      </LineChart>
    </div>
  );
};

export default App;