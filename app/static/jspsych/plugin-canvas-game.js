var jsPsychCanvasGame = (function (jspsych) {
  'use strict';

  const info = {
      name: "canvas-game",
      parameters: {
          game_data: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Game Data",
              default: {},// undefined,
          },
          /** The drawing function to apply to the canvas. Should take the canvas object as argument. */
          stimulus: {
              type: jspsych.ParameterType.FUNCTION,
              pretty_name: "Stimulus",
              default: "blg",// undefined,
          },
          /** Array containing the height (first value) and width (second value) of the canvas element. */
          canvas_size: {
              type: jspsych.ParameterType.INT,
              array: true,
              pretty_name: "Canvas size",
              default: [1000, 800],
          },
      },
  };
  /**
   * **canvas-game**
   *
   * jsPsych plugin for displaying a canvas stimulus and getting a keyboard response
   *
   * @author Chris Jungerius (modified from Josh de Leeuw)
   * @see {@link https://www.jspsych.org/plugins/jspsych-canvas-keyboard-response/ canvas-keyboard-response plugin documentation on jspsych.org}
   */
  class CanvasGamePlugin {
      constructor(jsPsych) {
          this.jsPsych = jsPsych;
      }

      trial(display_element, trial) {
          const ball_color = "green"
          const tool_color = "blue"
          const grasp_color = "red"
          const wall_color = "black"
          const grasp_rad = 3;
          const bound_color = "red"
          const goal_color = "green"

          //create and display html
          var new_html = '<div><canvas id="myCanvas" width="' + trial.canvas_size[0] + '" height="' + trial.canvas_size[1] + '" style="border:1px solid #000000;"></canvas></div>';
          display_element.innerHTML = new_html;

          //get canvas context
          const canvas = document.getElementById("myCanvas");
          const ctx = canvas.getContext("2d");

          //set og vars
          //starting state of this game
          const init_game_state = trial.game_data

          const helper1 = async(state) => {
            //console.log('start helper 1')
            await init_game(state)
            //console.log('end helper 1')
          }
          const helper2 = async(state) => {
            //console.log('start helper 2')
            await helper1(state)
            //console.log('end helper 2')
          }

          //function to initialize game for this trial
          function init_game(state) {
            //console.log("start init game")
            $.ajax({
              type: 'post',
              url:"/init_trial",
              data: JSON.stringify(state),
              contentType: "application/json; charset=utf-8",
              traditional: true,
            })
            //console.log("finish init game")
          }

          //i dont think this is working .___.
          helper2(init_game_state)

          var accept_request = true


          //callback to pass user input and get updated game state
          function get_game_update(user_data) {
            accept_request = false
            $.getJSON({
                url:"/callback",
                data: user_data,
                success: function(result) {
                    accept_request = true
                    draw(result)
                }
            })
          }
          function reset_user_input() {
              return {'ArrowLeft': 0, 'ArrowRight': 0, 'ArrowUp': 0, 'ArrowDown': 0, 'r': 0, 'f': 0, 'click': 0, 'click_x': null, 'click_y': null, 'Enter': 0};
          }

          //function to draw game
          //not drawing stuff
          function draw(dynamic_vars) {
            if(dynamic_vars["wall_test"]){
                console.log("hit wall!")
            }
            ctx.clearRect(0,0,canvas.width,canvas.height);

            var poss_tool_color = tool_color
            var ball_rad = init_game_state["ball_rad"]
            var wall_pos = init_game_state["wall_pos"]
            var poss_tool_locs = init_game_state["poss_tool_locs"]
            var goal_pos = init_game_state["goal_pos"]
            var bound_y = init_game_state["grasp_bound_y"]
            var bound_min_x = init_game_state["grasp_bound_min_x"]
            var bound_max_x = init_game_state["grasp_bound_max_x"]

            if(dynamic_vars["active_tool_idx"] >= 0) {
                poss_tool_color = "#3685c9"
            }

            //draw unchanging elements from init_game_state
            //walls
            for(var i=0; i<wall_pos.length; i++) {
                draw_poly(wall_pos[i], wall_color)
            }

            //goal
            draw_poly([[goal_pos[0], goal_pos[1]], [goal_pos[0] + goal_pos[2], goal_pos[1]], [goal_pos[0] + goal_pos[2], goal_pos[1] + goal_pos[3]], [goal_pos[0], goal_pos[1] + goal_pos[3]]], goal_color)
            //grasp bound
            draw_poly([[bound_min_x, bound_y], [bound_max_x, bound_y], [bound_max_x, bound_y-1], [bound_min_x, bound_y-1]], bound_color)

            //tool locs (maybe dim if there's an active tool, with selected outlined in black)
            for(var i=0; i<poss_tool_locs.length; i++) {
                var poss_tool = poss_tool_locs[i]
                for(var j=0; j<poss_tool.length; j++) {
                    var tool_part = poss_tool[j]
                    if (dynamic_vars["active_tool_idx"]==i) {
                        draw_poly(tool_part, tool_color)
                    } else {
                        draw_poly(tool_part, poss_tool_color) 
                    }
                } 
            }
            //whatever else to make it look nice

            //then draw dynamic_vars
            draw_circle(dynamic_vars["ball_pos"], ball_rad, ball_color)

            //this is not evaluating to true
            if (dynamic_vars["active_tool_idx"] >= 0) {
                //draw active tool
                var tool_parts = dynamic_vars["active_tool_vertices"]
                for(var i=0; i<tool_parts.length; i++) {
                    draw_poly(tool_parts[i], tool_color)
                }
                //draw grasp pos
                if (dynamic_vars["is_grasped"]) {
                    draw_circle(dynamic_vars["grasp_pos"], grasp_rad, grasp_color)
                }
            }
            if (dynamic_vars["success"]) {
                console.log("idk, celebrate or something!!")
            }

          }

          function draw_circle(pos, rad, color) {
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(pos[0], pos[1], rad, 0, 2*Math.PI);
            ctx.fill();
          }
          function draw_poly(vertices, color) {
            //console.log(vertices)
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.moveTo(vertices[0][0], vertices[0][1]);
            for(var i=1; i<vertices.length; i++) {
                ctx.lineTo(vertices[i][0],vertices[i][1]);
            }
            ctx.closePath();
            ctx.fill();
          }

          //starting values for vars
          var user_input = reset_user_input()
          var last_click = [null,null]
          var pressed_keys = new Set();
          var valid_keys = new Set(["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "r", "f", "Enter"]);

          //code goes here that will be run every second  

          //could also make this while (true), accept = true, set accept to false at start of get_game_update, set to true if success, and only call if success"
          setInterval(function(){ 
          //while(true) {
            //if (accept_request) {
            //add pressed keys and last click pos to dict
            user_input["click_x"] = last_click[0]
            user_input["click_y"] = last_click[1]
            if (last_click[0] != null) {
                user_input["click"] = 1
            }
            //update user input to have these as keys
            pressed_keys.forEach(k => {
                user_input[k] = 1
            });
            //make callback
            get_game_update(user_input)
            //reset stored input
            //pressed_keys = new Set()
            last_click = [null,null]
            user_input = reset_user_input()
            //}
          //}
          }, 5);


          // function to end trial when it is time
          const end_trial = () => {
              // kill any remaining setTimeout handlers
              this.jsPsych.pluginAPI.clearAllTimeouts();
              // kill keyboard listeners
              if (typeof keyboardListener !== "undefined") {
                  this.jsPsych.pluginAPI.cancelKeyboardResponse(keyboardListener);
              }
              // gather the data to store for the trial
              var trial_data = {
                  rt: response.rt,
                  response: response.key,
              };
              // clear the display
              display_element.innerHTML = "";
              // move on to the next trial
              this.jsPsych.finishTrial(trial_data);
          };

          // start the response listener
          // listen for user input (clicks and key presses)
          var start_time = performance.now()
          //record clicks inside canvas
          canvas.addEventListener("click", (e) => {
            const rect = canvas.getBoundingClientRect()
            var x = event.clientX - rect.left
            var y = event.clientY - rect.top
            last_click = [x, y]
          });
          //record clicks on buttons

          addEventListener('keydown', (e) => {
            //check if in valid keys, if not already in pressed then add
            if (valid_keys.has(e.key)) {
                e.preventDefault();
                var rt = Math.round(performance.now() - start_time);
                if (! pressed_keys.has(e.key)) {
                    pressed_keys.add(e.key)
                }
            }
          });

          
          addEventListener('keyup', (e) => {
            //if key up, check if in valid keys and then remove from set
            if (valid_keys.has(e.key)) {
                var rt = Math.round(performance.now() - start_time);
                if (pressed_keys.has(e.key)) {
                    pressed_keys.delete(e.key)
                }
            }
          });
          



          // hide stimulus if stimulus_duration is set
          /*
          if (trial.stimulus_duration !== null) {
              this.jsPsych.pluginAPI.setTimeout(() => {
                  display_element.querySelector("#jspsych-canvas-keyboard-response-stimulus").style.visibility = "hidden";
              }, trial.stimulus_duration);
          }
          // end trial if trial_duration is set
          if (trial.trial_duration !== null) {
              this.jsPsych.pluginAPI.setTimeout(() => {
                  end_trial();
              }, trial.trial_duration);
          }
          */
      }
      /*
      simulate(trial, simulation_mode, simulation_options, load_callback) {
          if (simulation_mode == "data-only") {
              load_callback();
              this.simulate_data_only(trial, simulation_options);
          }
          if (simulation_mode == "visual") {
              this.simulate_visual(trial, simulation_options, load_callback);
          }
      }
      simulate_data_only(trial, simulation_options) {
          const data = this.create_simulation_data(trial, simulation_options);
          this.jsPsych.finishTrial(data);
      }
      simulate_visual(trial, simulation_options, load_callback) {
          const data = this.create_simulation_data(trial, simulation_options);
          const display_element = this.jsPsych.getDisplayElement();
          this.trial(display_element, trial);
          load_callback();
          if (data.rt !== null) {
              this.jsPsych.pluginAPI.pressKey(data.response, data.rt);
          }
      }
      create_simulation_data(trial, simulation_options) {
          const default_data = {
              rt: this.jsPsych.randomization.sampleExGaussian(500, 50, 1 / 150, true),
              response: this.jsPsych.pluginAPI.getValidKey(trial.choices),
          };
          const data = this.jsPsych.pluginAPI.mergeSimulationData(default_data, simulation_options);
          this.jsPsych.pluginAPI.ensureSimulationDataConsistency(trial, data);
          return data;
      }
      */
  }
  CanvasGamePlugin.info = info;

  return CanvasGamePlugin;

})(jsPsychModule);
