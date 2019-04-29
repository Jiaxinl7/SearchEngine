import React, { Component } from "react";
import { Menu, Input, Button, Icon } from "semantic-ui-react";
import { withRouter } from "react-router-dom";
class NavBar extends Component {
  state = {};
  constructor(props) {
    super(props);
    this.state = {
      query: this.props.query
    };
    this.handleChange = this.handleChange.bind(this);
    this.navigateToHome = this.navigateToHome.bind(this);
    this.clickSearch = this.clickSearch.bind(this);
    this.navigateToHotEvent = this.navigateToHotEvent.bind(this);
  }
  navigateToHome = e => {
    e.preventDefault();
    this.props.history.push({
      pathname: "/"
    });
  };
  navigateToHotEvent = e => {
    e.preventDefault();
    this.props.history.push({
      pathname: "/hot_event"
    });
  };
  handleChange = e => {
    e.preventDefault();
    this.setState({ query: e.target.value });
  };
  clickSearch = e => {
    e.preventDefault();
    this.props.clickSearch(this.state.query);
  };
  render() {
    const { activeItem } = this.state;
    return (
      <Menu stackable>
        <Menu.Item>
          <img src="https://react.semantic-ui.com/logo.png" />
        </Menu.Item>

        <Menu.Item
          name="Home"
          active={activeItem === "Home"}
          onClick={this.navigateToHome}
        >
          Home
        </Menu.Item>
        <Menu.Item
          name="Hot Event"
          active={activeItem === "Source"}
          onClick={this.navigateToHotEvent}
        >
          Source
        </Menu.Item>

        <Menu.Item>
          <Input
            value={this.state.query}
            action={
              <Button icon onClick={this.clickSearch}>
                <Icon name="search" />
              </Button>
            }
            onChange={this.handleChange}
            placeholder="Search..."
          />
        </Menu.Item>
      </Menu>
    );
  }
}

export default withRouter(NavBar);
