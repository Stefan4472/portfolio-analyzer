import React from "react";
import { Line } from "react-chartjs-2";
import { Colors } from "chart.js";
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
import { ProcessedPortfolio } from "./Portfolio";

ChartJS.register(
  CategoryScale,
  Colors,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
);

export const kPlotOptions = {
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

function formDataset(processed: ProcessedPortfolio[]): ChartData<"line"> {
  console.log("Forming dataset wth data ", processed);
  if (processed.length === 0) {
    return {
      labels: [],
      datasets: [],
    };
  }

  const dates = processed[0].values.map((v) => v.date);
  return {
    labels: dates,
    datasets: processed.map((portfolio) => ({
      label: portfolio.name,
      data: portfolio.values.map((v) => v.value),
    })),
  };
}

interface PlotterProps {
  portfolios: ProcessedPortfolio[];
  // TODO: use a Javascript date library and pass in actual date objects.
  startDate: string;
  endDate: string;
}

export const PortfolioPlotter: React.FC<PlotterProps> = (props) => {
  return <Line options={kPlotOptions} data={formDataset(props.portfolios)} />;
};
