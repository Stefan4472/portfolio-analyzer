import axios from "axios";

const axiosInstance = axios.create({
  // TODO: change to relative URL.
  baseURL: "http://localhost:5000",
  headers: {
    "Content-type": "application/json",
    Accept: "application/json",
  },
});

export interface TickerValue {
  date: string;
  value: number;
}

export interface PortfolioValue {
  date: string;
  value: number;
}

class Endpoints {
  async getTicker(ticker: string): Promise<TickerValue[]> {
    const result = await axiosInstance.get(`/ticker/${ticker}`);
    return result.data as TickerValue[];
  }

  async processPortfolio(
    portfolioDefinition: string,
  ): Promise<PortfolioValue[]> {
    const result = await axiosInstance.post("/portfolio", portfolioDefinition);
    return result.data as PortfolioValue[];
  }
}

export default new Endpoints();
