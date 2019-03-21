import React, { Component } from "react";
import { Menu, List } from "semantic-ui-react";

class HotTopic extends Component {
  render() {
    return (
      <List link>
        <List.Item as="a">Hot Topic 1</List.Item>
        <List.Item as="a">Hot Topic 2</List.Item>
        <List.Item as="a">Hot Topic 3</List.Item>
        <List.Item as="a">Hot Topic 4</List.Item>
      </List>
    );
  }
}

export default HotTopic;
