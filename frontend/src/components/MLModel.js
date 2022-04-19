import React from 'react';
import Form from 'react-bootstrap/Form'
import FloatingLabel from 'react-bootstrap/FloatingLabel'
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/esm/Container';
import Toast from 'react-bootstrap/Toast'
import InfoImg from '../utilities/info-circle.svg'

class MLModel extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            showToast: false,
            num_infs:' 32',
            num_supp_sw: ' 2',
            op_penalty: ' 300',
            helped_sw: ' 4,1,2',
            data_frequency: 1,
        };

        this.setToast = this.setToast.bind(this)
    }

    setToast = () => {
        this.setState((state) => ({
            showToast: !state.showToast
        }));
    }

    runMLModel = (e) => {
        console.log("Clicked")
        console.log(this.props.topology)
        // const req = {
        //     method: "POST",
        //     headers: {"Content-Type": "application/json"},
        //     body: JSON.stringify({
        //         support_switches: this.state.support_switches,
        //         data_frequency: this.state.data_frequency,
        //     })
        // };
        // fetch("/api/model", req)
        //     .then((res) => res.json())
        //     .then((data) => console.log(data))
    }

    render() {
        return (
            <>
            <h3> 
            <Button variant="outline-secondary" onClick={this.setToast}>
                <img style = {{marginRight : 10 }} src={InfoImg} alt="info"/>
                Model...
            </Button>
            <Toast show={this.state.showToast} onClose={this.setToast}>
            <Toast.Header><strong className="me-auto">What does it do?</strong></Toast.Header>
                <Toast.Body>It configures the machine learning model config file. Then it runs the train model and the test.
                    
                </Toast.Body>
            </Toast>
            </h3>
            <Container>
                <Form className='d-grid gap-1'>
                    <FloatingLabel controlId="floatingText" label="Number of supportive Switches">
                        <Form.Control type="text" placeholder="Floating label select num_supp_sw" />
                    </FloatingLabel>
                    <FloatingLabel controlId="floatingText" label="Number of total interfaces">
                        <Form.Control type="text" placeholder="Floating label select num_infs" />
                        {/* TODO: Add validation */}
                    </FloatingLabel>
                    <FloatingLabel controlId="floatingText" label="Data Frequency">
                        <Form.Control type="text" placeholder="Floating label select data_frequency" />
                        {/* TODO: Add validation */}
                    </FloatingLabel>
                    <FloatingLabel controlId="floatingText" label="OverProvisoning Penalty">
                        <Form.Control type="text" placeholder="Floating label select op_penalty" />
                        {/* TODO: Add validation */}
                    </FloatingLabel>
                    <FloatingLabel controlId="floatingText" label="Helped Switches">
                        <Form.Control type="text" placeholder="Floating label select helped_sw" />
                        {/* TODO: Add validation */}
                    </FloatingLabel>
                    <Button className="ms-auto" variant="outline-success" onClick={this.runMLModel}>Run ML Model</Button>
                </Form>
            </Container>
            </>
        );
    }
}

export default MLModel;