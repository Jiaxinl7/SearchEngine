import React, { Component } from "react";
import SearchItem from "../components/SearchItem";
import HotTopic from "../components/HotTopic";
import NavBar from "../components/NavBar";
import { Grid, Container, Item, Pagination } from "semantic-ui-react";
import "../styles/ResultPage.css";
class ResultPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      query: this.props.location.state.query
    };
  }
  render() {
    var results = [];
    for (var i = 0; i < 5; i++) {
      results.push(<SearchItem />);
    }
    return (
      <div>
        <NavBar query={this.state.query} />
        <Grid>
          <Grid.Column width={12}>
            <div class="result-group">
              <Container textAlign="left">
                <Item.Group>{results}</Item.Group>
              </Container>
            </div>
          </Grid.Column>
          <Grid.Column width={4}>
            <HotTopic />
          </Grid.Column>
        </Grid>
        <Grid
          style={{ marginTop: "50px", marginBottom: "30px" }}
          textAlign="center"
        >
          <Pagination defaultActivePage={5} totalPages={10} />
        </Grid>
      </div>
    );
  }
}

export default ResultPage;
