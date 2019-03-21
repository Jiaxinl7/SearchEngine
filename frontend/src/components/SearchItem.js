import React, { Component } from "react";
import { Item } from "semantic-ui-react";
import "../styles/ResultPage.css";

const paragraph =
  "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.";
class SearchItem extends Component {
  constructor(props) {
    super(props);
    this.state = {
      header: this.props.header || "News Header",
      content: this.props.content || paragraph,
      source: this.props.source || "BBC",
      time: this.props.time || "2019-03-21",
      link: this.props.link || "http://www.google.com"
    };
  }
  render() {
    return (
      <Item>
        <Item.Content>
          <Item.Header>{this.state.header}</Item.Header>
          <Item.Meta>
            <span className="link">{this.state.link}</span>
            <span className="time">{this.state.time}</span>
            <span className="source">{this.state.source}</span>
          </Item.Meta>
          <Item.Description>{this.state.content}</Item.Description>
        </Item.Content>
      </Item>
    );
  }
}
export default SearchItem;
