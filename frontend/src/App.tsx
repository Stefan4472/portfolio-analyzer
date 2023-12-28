import React, { useState } from "react";
import Endpoints from "./Endpoints";
import { TickerValue } from "./Endpoints";
import "bootstrap/dist/css/bootstrap.min.css";

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
      position: "right" as const,
    },
    title: {
      display: false,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
    },
  },
};

const startingPortfolio = `
{
  "actions": [
    {
      "date": "2020-03-17",
      "ticker": "TSLA",
      "type": "Buy",
      "volume": 52,
      "price": 28.00
    }
  ]
}
`;
export const App: React.FC = () => {
  const [portfolioDefinition, setPortfolioDefinition] =
    useState<string>(startingPortfolio);
  const [data, setData] = useState<TickerValue[]>([]);

  function handleInput(e: React.ChangeEvent<HTMLTextAreaElement>) {
    // TODO: validate before setting value.
    setPortfolioDefinition(e.target.value);
  }

  function handleClick() {
    Endpoints.processPortfolio(portfolioDefinition).then((res) => {
      console.log(res);
      setData(res);
    });
  }

  function formDataset(tickerData: TickerValue[]): ChartData<"line"> {
    console.log("Forming dataset wth data ", tickerData);
    return {
      labels: tickerData.map((d: TickerValue) => d.date),
      datasets: [
        {
          label: "Portfolio",
          data: tickerData.map((d) => d.value),
          borderColor: "rgb(255, 99, 132)",
          backgroundColor: "rgba(255, 99, 132, 0.5)",
        },
      ],
    };
  }

  return (
    <div className="container">
      <div className="row">
        <div className="col">
          <Line options={options} data={formDataset(data)} />
        </div>
      </div>
      <div className="row">
        <div className="col">
          <div className="mb-3">
            <label htmlFor="portfolio-input" className="form-label">
              Portfolio Input
            </label>
            <textarea
              className="form-control"
              id="portfolio-input"
              defaultValue={startingPortfolio}
              rows={10}
              cols={80}
              onChange={handleInput}
            />
            <button className="btn btn-primary" onClick={handleClick}>
              Go
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
