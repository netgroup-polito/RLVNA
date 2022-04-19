export default class CreateTopology{
    
    constructor(){
        this.ctrl = {}
        this.sw = {}
        this.links = {}
        this.num_ctrl = 0
        this.num_sw = 0
        this.num_h = 0
        this.num_link = 0
    }

    increase_h(){
        this.num_h++
    }
    
    add_ctrl(){
        this.ctrl['c'+this.num_ctrl] = {}
        this.num_ctrl++
    }
    
    add_sw(){
        this.sw['s'+this.num_sw] = new Array()
        this.num_sw++
    }

    link_ctrl(ctrl, sw){
        this.ctrl[ctrl][sw] = this.sw[sw]
        //this.num_link++ //to ctrl 
    }

    link_h(sw, h){
        this.sw[sw].push(h)
        this.num_link++ //to switch
    }

    link_sw(src, dst){
        if(this.links[src] === undefined){ //the src has not extra links yet
            this.links[src] = new Array()
        }
        this.links[src].push(dst)
        this.num_link++ //TODO it's wrong in bidirectional link
    }

    //TODO delete host, sw, controller, link

}