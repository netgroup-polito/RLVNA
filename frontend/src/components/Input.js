import React from 'react';
import Settings from './Settings';
import Topology from './Topology';
import CreateTopology from '../utilities/CreateTopology';

export default class Input extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            topology: new CreateTopology(),
        };
    }
      
    render() {
        return (
            <>
                <Topology topology={this.state.topology} />
                <Settings topology={this.state.topology}/>
            </>
        );
    }
}