import React, { Component } from "react";
import { Menu, List, Header, Icon } from "semantic-ui-react";
import "../styles/ResultPage.css";
import { withRouter } from "react-router-dom";
class HotTopic extends Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.getEventNews = this.getEventNews.bind(this);
  }

  componentDidMount() {
    fetch("/search/hot/title/", {
      method: "POST",
      body: JSON.stringify({
        pagenum: 1
      })
    })
      .then(res => res.json())
      .then(res => {
        this.setState({
          results: res.results,
          totalPages: res.pagecount
        });
        console.log(this.state.results);
      });
  }

  getEventNews(e, docnum, title) {
    e.preventDefault();
    this.props.history.push({
      pathname: "/event",
      state: {
        docnum: docnum,
        title: title
      }
    });
  }
  render() {
    var results = [];
    var getEventNews = this.getEventNews;
    if (this.state.results != null) {
      this.state.results.forEach(function(result, i) {
        results.push(
          <List.Item
            as="a"
            onClick={e => getEventNews(e, result.docnum, result.title)}
            key={result.docnum}
          >
            <List.Icon
              name="newspaper outline"
              size="large"
              verticalAlign="middle"
            />
            <List.Content>
              <List.Header>{result.title}</List.Header>
              <List.Description>{result.pubtime}</List.Description>
            </List.Content>
          </List.Item>
        );
      });
    }

    return (
      <div>
        <Header as="h3">
          <Icon name="paper plane outline" />
          <Header.Content>Hot Events</Header.Content>
        </Header>
        <List link divided relaxed>
          {results}
        </List>
      </div>
    );
  }
}

export default withRouter(HotTopic);
