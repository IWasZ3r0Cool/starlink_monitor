import React, { useEffect, useState } from "react";
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from "recharts";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8080";

const App = () => {
  const [pings, setPings] = useState([]);
  const [speedTests, setSpeedTests] = useState([]);
  const [pingsError, setPingsError] = useState(null);
  const [speedTestsError, setSpeedTestsError] = useState(null);

  // Fetch Ping Data
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/pings`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log("Ping data fetched from API:", data); // Log the raw response
        if (data.length === 0) {
          setPingsError("No ping data available.");
        } else {
          setPings(data.map(([id, timestamp, target, success]) => ({
            id,
            timestamp,
            target,
            success,
          })));
        }
      })
      .catch((err) => {
        console.error("Error fetching ping data:", err);
        setPingsError("Failed to fetch ping data.");
      });

    // Fetch Speed Test Data
    fetch(`${API_BASE_URL}/api/speedtests`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log("Speed test data fetched from API:", data); // Log the raw response
        if (data.length === 0) {
          setSpeedTestsError("No speed test data available.");
        } else {
          setSpeedTests(data.map(([id, timestamp, download, upload, ping]) => ({
            id,
            timestamp,
            download,
            upload,
            ping,
          })));
        }
      })
      .catch((err) => {
        console.error("Error fetching speed test data:", err);
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
          data={pings.map((item) => ({
            timestamp: item.timestamp,
            success: item.success,
            target: item.target,
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
          data={speedTests.map((item) => ({
            timestamp: item.timestamp,
            download: item.download,
            upload: item.upload,
          }))}
        >
          <Line type="monotone" dataKey="download" stroke="#82ca9d" />
          <Line type="monotone" dataKey="upload" stroke="#8884d8" />
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