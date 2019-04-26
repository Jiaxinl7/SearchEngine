import React, { Component } from "react";
import {
  Button,
  Divider,
  Input,
  Segment,
  Header,
  Select,
  Icon
} from "semantic-ui-react";
import { Redirect, withRouter } from "react-router-dom";
import { ETIME } from "constants";

const options = [
  { key: "all", text: "All", value: "all" },
  { key: "nyt", text: "New York Times", value: "nyt" },
  { key: "cnn", text: "CNN", value: "cnn" },
  { key: "bbc", text: "BBC", value: "bbc" }
];

class Index extends Component {
  constructor(props) {
    super(props);
    this.state = {
      query: ""
    };
    this.clicksearch = this.clicksearch.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }
  handleChange = e => {
    e.preventDefault();
    this.setState({ query: e.target.value });
  };
  clicksearch = e => {
    e.preventDefault();
    this.props.history.push({
      pathname: "/result",
      state: {
        query: this.state.query
      }
    });
  };
  render() {
    return (
      <div style={{ marginTop: "150px" }}>
        <Header as="h2" icon textAlign="center">
          <Icon name="newspaper outline" circular />
          <Header.Content>Event Please</Header.Content>
        </Header>
        <Segment basic textAlign="center">
          <Input
            icon="search"
            type="text"
            onChange={this.handleChange}
            iconPosition="left"
            placeholder="Search News"
            action={{ color: "blue", content: "Search" }}
          >
            <Icon name="search" />
            <input />
            <Select compact options={options} defaultValue="all" />
            <Button primary type="submit" onClick={this.clicksearch}>
              Search
            </Button>
          </Input>

          <Divider horizontal>Or</Divider>

          <Button
            color="teal"
            content="Create New Event"
            icon="add"
            labelPosition="left"
          />
        </Segment>
      </div>
    );
  }
}

export default withRouter(Index);
