import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import React from "react";
import NavBar from "./components/NavBar";
import MarketVis from "./components/MarketVis";
import Footer from "./components/Footer";

function App() {
  return (
    <>
      <Router>
        <NavBar />
        <Switch>
          <Route path="/" exact component={MarketVis} />
        </Switch>
        <Footer />
      </Router>
    </>
  );
}

export default App;
