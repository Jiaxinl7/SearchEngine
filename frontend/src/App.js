import React, { Component } from "react";
import "./App.css";
import IndexPage from "./pages/IndexPage";
import NewsPage from "./pages/NewsPage";
import EventPage from "./pages/EventPage";
import HotEventPage from "./pages/HotEventPage";
import { Switch, Route, BrowserRouter } from "react-router-dom";

class App extends Component {
  render() {
    return (
      <div className="app-routes">
        <BrowserRouter>
          <Switch>
            <Route path="/news" component={NewsPage} />
            <Route path="/event" component={EventPage} />
            <Route path="/hot_event" component={HotEventPage} />
            <Route path="/" component={IndexPage} />
          </Switch>
        </BrowserRouter>
      </div>
    );
  }
}

export default App;
