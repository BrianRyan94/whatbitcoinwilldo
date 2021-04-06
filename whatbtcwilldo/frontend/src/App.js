import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import React from "react";
import NavBar from "./components/NavBar";
import MarketVis from "./components/MarketVis";

function App() {
  return (
    <>
      <Router>
        <NavBar />
        <Switch>
          <Route path="/" exact component={MarketVis} />
        </Switch>
      </Router>
    </>
  );
}

export default App;
