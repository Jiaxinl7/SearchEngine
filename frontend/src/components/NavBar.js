import React, { Component } from "react";
import { Menu, Input } from "semantic-ui-react";
import { Redirect, withRouter } from "react-router-dom";
class NavBar extends Component {
  state = {};
  constructor(props) {
    super(props);
    this.state = {
      query: this.props.query
    };
    this.handleChange = this.handleChange.bind(this);
    this.navigateToHome = this.navigateToHome.bind(this);
  }
  navigateToHome = e => {
    e.preventDefault();
    this.props.history.push({
      pathname: "/"
    });
  };
  handleChange = e => {
    e.preventDefault();
    this.setState({ query: e.target.value });
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
          name="Source"
          active={activeItem === "Source"}
          onClick={this.handleItemClick}
        >
          Source
        </Menu.Item>

        <Menu.Item>
          <Input
            className="icon"
            icon="search"
            value={this.state.query}
            onChange={this.handleChange}
            placeholder="Search..."
          />
        </Menu.Item>
      </Menu>
    );
  }
}

export default withRouter(NavBar);
