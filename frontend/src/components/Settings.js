import React from 'react';
import Container from 'react-bootstrap/esm/Container';
import Ryu from './Ryu';
import MLModel from './MLModel';
import NodeSSH from './NodeSSH';

class Settings extends React.Component{
    constructor(props){
        super(props);
        this.state = {};
    }

    render() {
        return (
            <>
            <h3>Settings...</h3>
            <Container>
                <Ryu />
                <MLModel topology={this.props.topology}/>
                <NodeSSH />
                <br />
                <br />
                <br />
            </Container>
            </>
        );
    }
}

export default Settings;