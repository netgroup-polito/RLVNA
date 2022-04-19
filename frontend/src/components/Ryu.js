import React from 'react';
import Form from 'react-bootstrap/Form'
import FloatingLabel from 'react-bootstrap/FloatingLabel'
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/esm/Container';
import Toast from 'react-bootstrap/Toast'
import Modal from 'react-bootstrap/Modal'

import InfoImg from '../utilities/info-circle.svg'

class Ryu extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            showToast: false,
            support_switches: '',
            data_frequency: 1,
            reverseButton: 'Run',
            showModal: false,
            data: 'OK',
            disableButton: false,
        };

        this.setToast = this.setToast.bind(this)
        this.handleClose = this.handleClose.bind(this)
        this.handleSwitches = this.handleSwitches.bind(this)
        this.handleFreq = this.handleFreq.bind(this)
    }

    setToast = () => {
        this.setState((state) => ({
            showToast: !state.showToast
        }));
    }

    handleClose = () => {
        this.setState((state) => ({
            showModal: false
        }));
    }

    handleSwitches = (e) => {
        this.setState({support_switches: e.target.value});
    }

    handleFreq = (e) => {
        this.setState({data_frequency: e.target.value});
    }

    runRyu = (e) => {
        this.setState((state) => ({
            disableButton: !state.disableButton
        }));
        const req = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                support_switches: this.state.support_switches,
                data_frequency: this.state.data_frequency,
            })
        };
        fetch("/api/ryu", req)
            .then((res) => {
                res.json()
                    .then((info) => {
                        this.setState((state) => ({
                            data: info,
                            showModal: true,
                            reverseButton: state.reverseButton == 'Run' ? 'Stop' : 'Run',
                            disableButton: !state.disableButton
                        }));
                    })
                    .catch( (err) => 'Error in downloading ssh command.')
            })
            .catch( (err) => 'Error in downloading ssh command.')
    }

    render() {
        return (
            <>
            <Modal show={this.state.showModal} onHide={this.handleClose}>
                <Modal.Header closeButton>
                <Modal.Title>Ryu controller status</Modal.Title>
                </Modal.Header>
                <Modal.Body>{this.state.data}</Modal.Body>
            </Modal>
            <h3>
            <Button variant="outline-secondary" onClick={this.setToast}>
                <img style = {{marginRight : 10 }} src={InfoImg} alt="info"/>
                Ryu... 
            </Button>
            <Toast show={this.state.showToast} onClose={this.setToast}>
            <Toast.Header><strong className="me-auto">What does it do?</strong></Toast.Header>
                <Toast.Body>It configures the ryu controller config file and run the controller inside the container.
                    Support switches should be in the form of: s0, s1, s2, s3
                    Data Frequency should be a positive integer and means that every X seconds the frequency the controller will ask the 
                    OVS switches the data.
                </Toast.Body>
            </Toast>
            </h3>
            <Container>
                <Form className='d-grid gap-1'>
                    <FloatingLabel controlId="supp_sw" label="Support Switches">
                        <Form.Control type="text" placeholder="Floating label select support_switches" onChange={(ev) => this.handleSwitches(ev)}/>
                    </FloatingLabel>
                    <FloatingLabel controlId="data_freq" label="Data Frequency">
                        <Form.Control type="text" placeholder="Floating label select data_frequency" onChange={(ev) => this.handleFreq(ev)}/>
                        {/* TODO: Add validation */}
                    </FloatingLabel>
                    {/* TODO handle Stop (killall) */}
                    <Button className="ms-auto" variant="outline-success" onClick={this.runRyu} disabled={this.state.disableButton} >{this.state.reverseButton} Ryu Controller</Button>
                </Form>
            </Container>
            </>
        );
    }
}

export default Ryu;