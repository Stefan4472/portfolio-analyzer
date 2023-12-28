import React, { useState } from "react";
import Endpoints from "./Endpoints";
import "bootstrap/dist/css/bootstrap.min.css";
import { PortfolioSelector } from "./PortfolioSelector";
import { highTechPortfolio, teslaPortfolio } from "./Defaults";
import { PortfolioPlotter } from "./PortfolioPlotter";
import { Portfolio, ProcessedPortfolio } from "./Portfolio";
import { Button } from "react-bootstrap";

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
    const processed: ProcessedPortfolio[] = [];
    for (const portfolio of portfolios) {
      Endpoints.processPortfolio(portfolio.actions).then((res) => {
        processed.push({ name: portfolio.name, values: res });
      });
    }
    console.log("Updating processedPortfolios");
    // TODO: the problem here is that we call setProcessedPortfolios() before
    // without actually waiting for the RPCs to return. We need to somehow
    // send all calls, then await them, *then* set the state.
    setProcessedPortfolios(processed);
  }

  return (
    <div className="container">
      <div className="row">
        <div className="col">
          <PortfolioPlotter portfolios={processedPortfolios} />
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
          <Button onClick={handlePlotAllPortfolios}>Update chart</Button>
        </div>
      </div>
    </div>
  );
};
