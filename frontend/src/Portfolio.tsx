import { PortfolioValue } from "./Endpoints";

export interface Portfolio {
  name: string;
  // Raw string of JSON actions.
  actions: string;
}

export interface ProcessedPortfolio {
  name: string;
  values: PortfolioValue[];
}
