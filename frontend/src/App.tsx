import React, { useState } from "react";
import Endpoints from "./Endpoints";
import "bootstrap/dist/css/bootstrap.min.css";
import { PortfolioSelector } from "./PortfolioSelector";
import { highTechPortfolio, teslaPortfolio } from "./Defaults";
import { PortfolioPlotter } from "./PortfolioPlotter";
import { Portfolio, ProcessedPortfolio } from "./Portfolio";
import { Button, Form } from "react-bootstrap";

const kStartingPortfolios: Portfolio[] = [
  // {name: "Total Market", actions: totalMarketPortfolio},
  { name: "High Tech", actions: highTechPortfolio },
  { name: "Tesla", actions: teslaPortfolio },
];

export const App: React.FC = () => {
  // The portfolios known to the app.
  const [portfolios, setPortfolios] =
    useState<Portfolio[]>(kStartingPortfolios);
  // The name of the portfolio (from `portfolios`) that is currently being edited.
  const [selectedPortfolioName, setSelectedPortfolio] = useState<string>(
    kStartingPortfolios[0].name,
  );
  // The *actions* of the portfolio that is currently being edited.
  const [currentlyEditing, setCurrentlyEditing] = useState<string>(
    kStartingPortfolios[0].actions,
  );
  // The portfolio data that was processed by the backend.
  const [processedPortfolios, setProcessedPortfolios] = useState<
    ProcessedPortfolio[]
  >([]);
  // The start date to plot ("YYYY-MM-DD").
  const [startDate, setStartDate] = useState<string>("2020-01-01");
  // The end date to plot ("YYYY-MM-DD").
  const [endDate, setEndDate] = useState<string>("2024-01-01");

  function handlePortfolioSelected(newSelection: string) {
    setSelectedPortfolio(newSelection);
    setCurrentlyEditing(getPortfolio(newSelection).actions);
  }

  function handleChangeCurrentlyEditedPortfolio(
    e: React.ChangeEvent<HTMLTextAreaElement>,
  ) {
    setCurrentlyEditing(e.target.value);
  }

  function handleSaveCurrentlyEditedPortfolio() {
    // TODO: validate JSON
    const updatedPortfolios: Portfolio[] = portfolios.map((p) => {
      if (p.name === selectedPortfolioName) {
        return { name: selectedPortfolioName, actions: currentlyEditing };
      } else {
        return p;
      }
    });
    setPortfolios(updatedPortfolios);
  }

  function getPortfolio(name: string): Portfolio {
    for (const p of portfolios) {
      if (p.name === name) {
        return p;
      }
    }
    throw new Error("No such portfolio: " + selectedPortfolioName);
  }

  function handlePlotAllPortfolios() {
    if (startDate === undefined || endDate === undefined) {
      alert("You must define 'Start Date' and 'End Date' first.");
      return;
    }
    if (startDate < "2000" || endDate < "2000") {
      alert("This application does not support dates before the year 2000.");
      return false;
    }
    if (startDate >= endDate) {
      alert("'Start Date' must come before 'End Date'.");
      return;
    }

    const processed: ProcessedPortfolio[] = [];
    for (const portfolio of portfolios) {
      Endpoints.processPortfolio(portfolio.actions, startDate, endDate).then(
        (res) => {
          processed.push({ name: portfolio.name, values: res });
        },
      );
    }
    console.log("Updating processedPortfolios");
    // TODO: the problem here is that we call setProcessedPortfolios() before
    // without actually waiting for the RPCs to return. We need to somehow
    // send all calls, then await them, *then* set the state.
    setProcessedPortfolios(processed);
  }

  function handleStartDateChanged(date: string) {
    if (date !== "" && date !== undefined) {
      setStartDate(date);
    }
  }

  function handleEndDateChanged(date: string) {
    if (date !== "" && date !== undefined) {
      setEndDate(date);
    }
  }

  return (
    <div className="container">
      <div className="row">
        <div className="col">
          <PortfolioPlotter
            portfolios={processedPortfolios}
            startDate={startDate}
            endDate={endDate}
          />
        </div>
      </div>
      <div className="row">
        <div className="col-md-3">
          <PortfolioSelector
            portfolioNames={portfolios.map((p) => p.name)}
            selectedPortfolio={selectedPortfolioName}
            onSelectionChanged={(newSelection) => {
              handlePortfolioSelected(newSelection);
            }}
          />
        </div>
        <div className="col-md-6">
          <textarea
            className="form-control"
            id="portfolio-input"
            value={currentlyEditing}
            rows={10}
            cols={80}
            onChange={handleChangeCurrentlyEditedPortfolio}
          />
          <Button onClick={handleSaveCurrentlyEditedPortfolio}>Save</Button>
        </div>
        <div className="col-md-3">
          <Form.Label htmlFor="inputStartDate">Start Date</Form.Label>
          <Form.Control
            type="date"
            id="startDate"
            aria-describedby="inputStartDate"
            value={startDate}
            onChange={(e) => {
              handleStartDateChanged(e.target.value);
            }}
          />
          <Form.Label htmlFor="inputEndDate">End Date</Form.Label>
          <Form.Control
            type="date"
            id="endDate"
            aria-describedby="inputEndDate"
            value={endDate}
            onChange={(e) => {
              handleEndDateChanged(e.target.value);
            }}
          />
          <Button onClick={handlePlotAllPortfolios}>Update chart</Button>
        </div>
      </div>
    </div>
  );
};
