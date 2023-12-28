import React from "react";
import { ListGroup } from "react-bootstrap";

interface SelectorProps {
  portfolioNames: string[];
  selectedPortfolio: string;
  onSelectionChanged: (newSelection: string) => void;
}

export const PortfolioSelector: React.FC<SelectorProps> = (props) => {
  return (
    <ListGroup>
      {props.portfolioNames.map((name) => (
        <ListGroup.Item
          action
          key={name}
          active={name === props.selectedPortfolio}
          onClick={() => {
            props.onSelectionChanged(name);
          }}
        >
          {name}
        </ListGroup.Item>
      ))}
    </ListGroup>
  );
};
