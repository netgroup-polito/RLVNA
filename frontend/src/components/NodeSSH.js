import React from 'react';
import Form from 'react-bootstrap/Form'
import ListGroup from 'react-bootstrap/ListGroup'
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/esm/Container';
import Toast from 'react-bootstrap/Toast'
import InfoImg from '../utilities/info-circle.svg'

class NodeSSH extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            showToast: false,
            placeholder: ['ssh nodes command...'],
            disableButton: false
        };

        this.setToast = this.setToast.bind(this)
        this.getSSH = this.getSSH.bind(this)
    }

    setToast = () => {
        this.setState((state) => ({
            showToast: !state.showToast
        }));
    }

    getSSH = (e) => {
        this.setState(() => ({
            disableButton: true
        }));
        const req = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({file: 'login'})
        };
        fetch("/api/download", req)
            .then((res) => {
                this.setState(() => ({
                    disableButton: false
                }));
                res.json()
                    .then((info) => {
                        this.setState(() => ({
                            placeholder: info
                        }));
                    })
                    .catch( (err) => 'Error in downloading ssh command.')
            })
            .catch( (err) => 'Error in downloading ssh command.')
    }

    render() {
        return (
            <>
            <h3> 
            <Button variant="outline-secondary" onClick={this.setToast}>
                <img style = {{marginRight : 10 }} src={InfoImg} alt="info"/>
                SSH Nodes...
            </Button>
            <Toast show={this.state.showToast} onClose={this.setToast}>
            <Toast.Header><strong className="me-auto">What does it do?</strong></Toast.Header>
                <Toast.Body>You can log inside the ssh machines and run the traffic you prefer.
                    Some examples are in: https://github.com/Enrico-git/NGI-support/
                </Toast.Body>
            </Toast>
            </h3>
            <Container>
                <Form className='d-grid gap-1'>                    
                    <ListGroup>
                        {this.state.placeholder.map((input, index) => 
                            <ListGroup.Item key={index}>{input}</ListGroup.Item>                    
                        )}
                    </ListGroup>                    
                    <Button className="ms-auto" variant="outline-success" onClick={this.getSSH} disabled={this.state.disableButton}>get SSH</Button>
                </Form>
            </Container>
            </>
        );
    }
}

export default NodeSSH;