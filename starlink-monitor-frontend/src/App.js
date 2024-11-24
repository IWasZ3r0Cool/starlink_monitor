import React, { useEffect, useState } from "react";
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from "recharts";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8080";

const App = () => {
  const [pings, setPings] = useState([]);
  const [speedTests, setSpeedTests] = useState([]);
  const [pingsError, setPingsError] = useState(null);
  const [speedTestsError, setSpeedTestsError] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/pings`)
      .then((res) => res.json())
      .then((data) => setPings(data))
      .catch((err) => {
        console.error("Failed to fetch pings:", err);
        setPingsError("Failed to fetch ping data.");
      });

    fetch(`${API_BASE_URL}/api/speedtests`)
      .then((res) => res.json())
      .then((data) => setSpeedTests(data))
      .catch((err) => {
        console.error("Failed to fetch speedtests:", err);
        setSpeedTestsError("Failed to fetch speed test data.");
      });
  }, []);

  return (
    <div>
      <h1>Starlink Monitor</h1>

      <h2>Ping Results</h2>
      {pingsError ? (
        <div style={{ color: "red" }}>{pingsError}</div>
      ) : (
        <LineChart
          width={600}
          height={300}
          data={pings.map(([id, timestamp, target, success]) => ({
            timestamp,
            success,
          }))}
        >
          <Line type="monotone" dataKey="success" stroke="#8884d8" />
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
        </LineChart>
      )}

      <h2>Speed Test Results</h2>
      {speedTestsError ? (
        <div style={{ color: "red" }}>{speedTestsError}</div>
      ) : (
        <LineChart
          width={600}
          height={300}
          data={speedTests.map(([id, timestamp, download, upload]) => ({
            timestamp,
            download,
          }))}
        >
          <Line type="monotone" dataKey="download" stroke="#82ca9d" />
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
        </LineChart>
      )}
    </div>
  );
};

export default App;