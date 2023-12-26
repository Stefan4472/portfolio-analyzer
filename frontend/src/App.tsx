import React, { useState } from "react";
import Endpoints from "./Endpoints";
import { TickerValue } from "./Endpoints";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
);

export const options = {
  responsive: true,
  plugins: {
    legend: {
      position: "top" as const,
    },
    title: {
      display: true,
      text: "Chart.js Line Chart",
    },
  },
  scales: {
    y: {
      beginAtZero: true,
    },
  },
};

export const App: React.FC = () => {
  const [ticker, setTicker] = useState<string>("GOOG");
  const [data, setData] = useState<TickerValue[]>([]);

  function handleInput(e: React.ChangeEvent<HTMLInputElement>) {
    setTicker(e.target.value);
  }

  function handleClick() {
    Endpoints.getTicker(ticker).then((res) => {
      setData(res);
    });
  }

  function formDataset(tickerData: TickerValue[]): ChartData<"line"> {
    console.log("Forming dataset wth data ", tickerData);
    return {
      labels: tickerData.map((d: TickerValue) => d.date),
      datasets: [
        {
          label: "GOOG",
          data: tickerData.map((d) => d.value),
          borderColor: "rgb(255, 99, 132)",
          backgroundColor: "rgba(255, 99, 132, 0.5)",
        },
      ],
    };
  }

  return (
    <div>
      <h1>Hello world.</h1>
      <input onChange={handleInput} />
      <button onClick={handleClick}>Click me.</button>
      <Line options={options} data={formDataset(data)} />;
    </div>
  );
};
