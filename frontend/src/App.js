import React, { Component } from "react";
import "./App.css";
import IndexPage from "./pages/IndexPage";
import ResultPage from "./pages/ResultPage";
import { Switch, Route, BrowserRouter } from "react-router-dom";

class App extends Component {
  render() {
    return (
      <div className="app-routes">
        <BrowserRouter>
          <Switch>
            <Route path="/result" component={ResultPage} />
            <Route path="/" component={IndexPage} />
          </Switch>
        </BrowserRouter>
      </div>
    );
  }
}

export default App;
