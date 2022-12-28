var jsPsychCanvasGame = (function (jspsych) {
  'use strict';

  const info = {
      name: "canvas-game",
      parameters: {
          /** The drawing function to apply to the canvas. Should take the canvas object as argument. */
          stimulus: {
              type: jspsych.ParameterType.FUNCTION,
              pretty_name: "Stimulus",
              default: "blah",// undefined,
          },
          /** Array containing the key(s) the subject is allowed to press to respond to the stimulus. */
          choices: {
              type: jspsych.ParameterType.KEYS,
              pretty_name: "Choices",
              default: "ALL_KEYS",
          },
          /** Any content here will be displayed below the stimulus. */
          prompt: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Prompt",
              default: null,
          },
          /** How long to show the stimulus. */
          stimulus_duration: {
              type: jspsych.ParameterType.INT,
              pretty_name: "Stimulus duration",
              default: null,
          },
          /** How long to show trial before it ends. */
          trial_duration: {
              type: jspsych.ParameterType.INT,
              pretty_name: "Trial duration",
              default: null,
          },
          /** If true, trial will end when subject makes a response. */
          response_ends_trial: {
              type: jspsych.ParameterType.BOOL,
              pretty_name: "Response ends trial",
              default: true,
          },
          /** Array containing the height (first value) and width (second value) of the canvas element. */
          canvas_size: {
              type: jspsych.ParameterType.INT,
              array: true,
              pretty_name: "Canvas size",
              default: [500, 500],
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

          //create and display html
          var screen_width = 800;
          var screen_height = 600;
          var new_html = '<div><canvas id="myCanvas" width="' + screen_width + '" height="' + screen_height + '" style="border:1px solid #000000;"></canvas></div>';
          display_element.innerHTML = new_html;

          //get canvas context
          const canvas = document.getElementById("myCanvas");
          const ctx = canvas.getContext("2d");

          //set og vars
          var circle_pos = [100,50];

          //function to draw game
          function draw() {
            ctx.clearRect(0,0,canvas.width,canvas.height);
            ctx.beginPath();
            ctx.arc(circle_pos[0],circle_pos[1],10,0,2*Math.PI);
            ctx.stroke();
          }

          //callback to pass user input and get updated game state
          function cb(user_data) {
            $.getJSON({
                url:"/callback",
                data: {'user_data': user_data},
                success: function(result) {
                    update_game(result)
                }
            })
          }
          //update canvas vars based on pygame gamestate
          function update_game(game_state) {
              circle_pos = [circle_pos[0]+.1, circle_pos[1]];
              draw();
          }

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

          // function to handle responses by the subject
          var after_response = (info) => {
              //get info.key and info.rt 
              console.log("here");
              console.log(info)
              //if we do 10000, things get ugly
              for (var i=0;i<10;i++) {
                cb(info.key);
              }
          };
          // start the response listener
          if (trial.choices != "NO_KEYS") {
              var keyboardListener = this.jsPsych.pluginAPI.getKeyboardResponse({
                  callback_function: after_response,
                  valid_responses: trial.choices,
                  rt_method: "performance",
                  persist: true,
                  allow_held_key: true,
              });
          }

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
