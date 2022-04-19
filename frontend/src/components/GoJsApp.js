
import React from 'react';

import * as gos from 'gojs';
import { ReactDiagram, ReactPalette } from 'gojs-react';
import '../utilities/styles.css';

/**
 * Diagram initialization method, which is passed to the ReactDiagram component.
 * This method is responsible for making the diagram and initializing the model and any templates.
 * The model's data should not be set here, as the ReactDiagram component handles that via the other props.
 */

// render function...
export default class GoJsApp extends React.Component{
  constructor(props){
    super(props);
    this.state = {
        topology: props.topology
    };
  }

  initDiagram = () => {
    const $ = gos.GraphObject.make;
    // set your license key here before creating the diagram: go.Diagram.licenseKey = "...";
    const diagram =
      $(gos.Diagram,
        {
          'undoManager.isEnabled': true,  // must be set to allow for model change listening
          // 'undoManager.maxHistoryLength': 0,  // uncomment disable undo/redo functionality
          allowDelete: false, // TODO remove this and handle the deletion! https://gojs.net/latest/intro/commands.html
          model: $(gos.GraphLinksModel,
            {
              addNodeData: true,
              linkKeyProperty: 'key'  // IMPORTANT! must be defined for merges and data sync when using GraphLinksModel
            })
  
        });
      // when the document is modified, add a "*" to the title and enable the "Save" button
  
    // define a simple Node template
    diagram.nodeTemplate =
      $(gos.Node, 'Auto',  // the Shape will go around the TextBlock
        $(gos.Shape, 'RoundedRectangle',
        new gos.Binding('location', 'loc', gos.Point.parse).makeTwoWay(gos.Point.stringify),
          { fill: 'white', portId: "", fromLinkable: true, toLinkable: true, strokeWidth: 0 },
          // Shape.fill is bound to Node.data.color
          new gos.Binding('fill', 'color')), 
        $(gos.TextBlock,
          { margin: 8, editable: false },  // some room around the text
          new gos.Binding('text', "key").makeTwoWay()
        ),
      );
    // define link template
    diagram.linkTemplate =
        $(gos.Link,{relinkableFrom: true, relinkableTo: true},
          $(gos.Shape),
          $(gos.Shape, {toArrow: "Line"})
        )
    diagram.toolManager.relinkingTool.fromHandleArchetype =
        $(gos.Shape,"Diamond", {desiredSize: new gos.Size(9,9), stroke: 'green', fill: 'lime', segmentIndex: 0});
    diagram.toolManager.relinkingTool.toHandleArchetype =
        $(gos.Shape,"Diamond", {desiredSize: new gos.Size(9,9), stroke: 'red', fill: 'pink', segmentIndex: -1});
  
    
    return diagram;
  }
  // initiates side palete for draggable nodes
  
  initPalette = () => {
    const $ = gos.GraphObject.make;
    var myPalette = $(gos.Palette, {
      // model: $(go.GraphLinksModel, {
      //   linkKeyProperty: "key" // IMPORTANT! must be defined for merges and data sync when using GraphLinksModel
      // }),
      layout: $(gos.GridLayout, {
        cellSize: new gos.Size(100, 100),
        wrappingColumn:1,
      })
    });
    
    myPalette.nodeTemplate = $(
      gos.Node,
      "Horizontal",
      $(
        gos.Shape,
        { margin:25, strokeWidth: 4, width: 100, height: 100, fill: "white" },
        new gos.Binding("fill", "color")
      ),
      $(gos.TextBlock, new gos.Binding("text", "title"))
    );
  
    return myPalette;
  }
  
  /**
   * This function handles any changes to the GoJS model.
   * It is here that you would make any updates to your React state.
   */
  handleModelChange = (changes)  => {
    if (changes.modifiedLinkData != undefined){
      let from = changes.modifiedLinkData[0].from;
      let to = changes.modifiedLinkData[0].to;
  
      console.log("from",from)
      console.log("to",to)
      
      if ((from.startsWith('c')) && (to.startsWith('s'))) {
        this.props.topology.link_ctrl(from, to)
      }else if ((from.startsWith('s')) && (to.startsWith('s'))){
        this.props.topology.link_sw(from, to)
      }else if ((from.startsWith('s')) && (to.startsWith('h'))){
        this.props.topology.link_h(from, to)
      }
      //NOTE: 'From' could not start from h -> TODO: return Error
      // could not be c - c 
    }else if (changes.insertedNodeKeys != undefined){
      console.log(changes.insertedNodeKeys)
      if (changes.insertedNodeKeys[0].startsWith('c')){
        // if (this.props.topology.num_ctrl == 0)
          this.props.topology.add_ctrl();
        // else
        //   //UNDO graphycally
        //   ;
        console.log(this)
        // console.log(this.diagram.commandHandler)
      }else if (changes.insertedNodeKeys[0].startsWith('s')){
        this.props.topology.add_sw()
      } else if (changes.insertedNodeKeys[0].startsWith('h')){
        this.props.topology.increase_h()
      }
      this.setState(() => ({
        topology: this.props.topology,
      }));
    }
    console.log(JSON.stringify(this.props.topology))
  }

  render() {
    return (
      <div style={{display: "flex"}}>

        <ReactPalette
          initPalette={this.initPalette}
          divClassName="paletteComponent"
          nodeDataArray={[
            { key: 'c'+this.props.topology.num_ctrl, color: "grey", title: "controller"},
            { key: 's'+this.props.topology.num_sw, color: "lightgreen", title: "switch"},
            { key: 'h'+this.props.topology.num_h, color: "lightblue", title: "host", to: false}
          ]}
        />

        <ReactDiagram
          initDiagram={this.initDiagram}
          divClassName='diagram-component'
          onModelChange={this.handleModelChange}
          topology={this.props.topology}
        />
      </div>
    );
  }
} ;

// export default GoJsApp;
