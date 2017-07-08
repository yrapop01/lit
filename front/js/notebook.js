/*
 * Requires editor.js to be loaded!
 */

function guid() {
  /* from https://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript */
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
}

function replaceAll(str, find, replace) {
    /* from https://stackoverflow.com/questions/1144783/how-to-replace-all-occurrences-of-a-string-in-javascript */
    return str.replace(new RegExp(find, 'g'), replace);
}

function Cell(anchor, position, notebook) {
    CELL_HTML = "<div class='row' id='top-{ID}' style='margin-bottom: 1.5em'><div class='col-xs-12 idle'>" +

                '<div style="position: absolute; top: -10px; left: 50%; margin-left: -175px; width: 350px; text-align: center">' +
                '<a href="#" class="controls"><span class="glyphicon glyphicon-play"></span></a> ' +
                '<a href="#" class="controls"><span class="glyphicon glyphicon-stop"></span></a> ' +
                '<a href="#" class="controls"><span class="glyphicon glyphicon-plus"></span></a> ' +
                '<a href="#" class="controls"><span class="glyphicon glyphicon-erase"></span></a> ' +
                '<a href="#" class="controls"><span class="glyphicon glyphicon-chevron-up"></span></a> ' +
                '<a href="#" class="controls"><span class="glyphicon glyphicon-chevron-down"></span></a> ' +
                '<a href="#" class="controls"><span class="glyphicon glyphicon-scissors"></span></a> ' +
                '<a href="#" class="controls"><span class="glyphicon glyphicon-wrench"></span></a>' +
                '</div>' +

                "<pre tabindex='0' style='margin-bottom: 0px'>" +
                "<code class='python code' contenteditable='true' id='editor-{ID}' spellcheck='false'></code>" +
                "</pre>" +

                "<div id='run-{ID}' style='display: none'>" +
                "<pre id='output-{ID}' class='well well-sm' style='margin-bottom: 0'></pre>" +
                "<table class='table table-bordered' style='margin-top: 0; font-size: x-small'>" +
                    "<tr><td id='item-{ID}' style='white-space: pre'>Item: 0</td>" +
                    "<td id='state-{ID}' style='width: 100%'>State: Idle</td>" + 
                    "<td id='order-{ID}' style='white-space: pre'>Order: 0</td></tr>" +
                "</table>" +
                "</div>" +
                "</div></div>"

    function cell(anchor, position, notebook) {
        this.guid = guid();
        this.nextCell = null;
        this.prevCell = null;
        this.state = 'idle';

        this.notebook = notebook
        notebook[this.guid] = this;

        var html = CELL_HTML;
        var html = replaceAll(html, "{ID}", this.guid);

        anchor.insertAdjacentHTML(position, html);

        this.editorNode = document.getElementById('editor-' + this.guid);
        this.outputNode = document.getElementById('output-' + this.guid);
    
        this.itemNode = document.getElementById('item-' + this.guid);
        this.stateNode = document.getElementById('state-' + this.guid);
        this.orderNode = document.getElementById('order-' + this.guid);

        this.runNode = document.getElementById('run-' + this.guid);
        this.topNode = document.getElementById('top-' + this.guid);

        this.editor = Editor(this.editorNode);
    }

    cell.prototype.focus = function() {
        this.editorNode.focus();
    }

    cell.prototype.detach = function() {
        if (this.prevCell)
            this.prevCell.nextCell = this.nextCell;
        if (this.nextCell)
            this.nextCell.prevCell = this.prevCell;
    }

    cell.prototype.attach = function(cell) {
        if (this.nextCell === cell)
            return cell;
        cell.detach()
        if (this.nextCell)
            this.nextCell.prevCell = cell;

        cell.nextCell = this.nextCell;
        cell.prevCell = this;
        this.nextCell = cell;      
    }

    cell.prototype.next = function() {
        return this.nextCell;
    }

    cell.prototype.code = function() {
        return this.editor.node.innerText;
    }

    cell.prototype.change_status = function(state) {
        if (state)
            this.state = state;
        else
            this.state = 'Idle';

        var state_html = this.state;
        if (this.state == 'Running') {
            this.runNode.style.display = 'block';
            state_html = '<span style="color: red">Running</span>';
        }

        this.stateNode.innerHTML = 'State: ' + state_html;
    }

    cell.prototype.write = function(answer) {
        this.outputNode.innerHTML += answer;
    }

    cell.prototype.clear = function(answer) {
        this.runNode.style.display = 'none';
        this.outputNode.innerText = '';
    }

    cell.prototype.forward = function() {
        if (this.nextCell) {
            this.nextCell.focus()
            return;
        }

        var cell = Cell(this.topNode, 'afterend', this.notebook);

        cell.prevCell = this;
        this.nextCell = cell;

        cell.focus();
    }

    var c = new cell(anchor, position, notebook);

    c.editorNode.addEventListener('keydown', function(e) {
        var key = e.keyCode || e.charCode;
        if (key == 13 && e.shiftKey) {
            e.preventDefault();
            c.forward();
            if (c.notebook.events.submit)
                c.notebook.events.submit(c);
        }
    });

    return c;
}

function Notebook(container) {
    var notebook = {events: {}, cells: {}};
    var cell = Cell(container, 'beforeend', notebook);

    return notebook;
}
