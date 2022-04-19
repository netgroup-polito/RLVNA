import React from 'react';
import Container from 'react-bootstrap/esm/Container';
import GoJsApp from './GoJsApp';
import Button from 'react-bootstrap/Button';

class Topology extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            topology: props.topology,
            disabled: false
        };

    }
 
    createTopology = () => {
        console.log(this.state.topology)
        const req = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                topology: JSON.stringify(this.state.topology)
            })
        };
        fetch("/api/topology", req)
            .then((res) => res.json())
            .then((data) => console.log(data)) // TODO feedback to client. Error in fail.
                                                // TODO disable other buttons at beginning. 
                                                // *only* if topology is reserved should be 
                                                // enabled
        this.setState((state) => ({
            disabled: !state.disabled
        }));
    }

    render() {
        return (
            <>
            <h3>Topology...</h3>
            <Container>
                <GoJsApp topology = {this.props.topology}  />
                <Button className="ms-auto" variant="outline-success" onClick={this.createTopology} disabled={this.state.disabled}>Create Topology</Button>
                {/* <Button className="ms-auto" variant="outline-success" onClick={this.createTopology}>Create Topology</Button> */}
            </Container>
            </>
        );
    }
}

export default Topology;