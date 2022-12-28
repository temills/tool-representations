var jsPsychDotTask = (function (jspsych) {
  'use strict';

  const info = {
      name: "dot-task",
      parameters: {
          /** The HTML string to be displayed */
          stimulus: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Stimulus",
              default: undefined,
          },
          /** Array containing the label(s) for the button(s). */
          choices: {
              type: jspsych.ParameterType.STRING,
              pretty_name: "Choices",
              default: undefined,
              array: true,
          },
          /** The HTML for creating button. Can create own style. Use the "%choice%" string to indicate where the label from the choices parameter should be inserted. */
          button_html: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Button HTML",
              default: '<button class="jspsych-btn">%choice%</button>',
              array: true,
          },
          /** Any content here will be displayed under the button(s). */
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
          /** How long to show the trial. */
          trial_duration: {
              type: jspsych.ParameterType.INT,
              pretty_name: "Trial duration",
              default: null,
          },
          /** The vertical margin of the button. */
          margin_vertical: {
              type: jspsych.ParameterType.STRING,
              pretty_name: "Margin vertical",
              default: "0px",
          },
          /** The horizontal margin of the button. */
          margin_horizontal: {
              type: jspsych.ParameterType.STRING,
              pretty_name: "Margin horizontal",
              default: "8px",
          },
          /** If true, then trial will end when user responds. */
          response_ends_trial: {
              type: jspsych.ParameterType.BOOL,
              pretty_name: "Response ends trial",
              default: true,
          },
          /** dot positions */
          dot_positions: {
            type: jspsych.ParameterType.Int,
            pretty_name: "Dot positions",
            default: null,
          },
          /** rectangle dimensions, [w,h] */
          rect_dims: {
            type: jspsych.ParameterType.Int,
            pretty_name: "Rectangle dimensions",
            default: null,
          },
          /** dot radius */
          dot_radius: {
            type: jspsych.ParameterType.Int,
            pretty_name: "radius of dots",
            default: null,
          },
          /** dot radius */
          dot_color: {
            type: jspsych.ParameterType.Int,
            pretty_name: "color of dots",
            default: null,
          }
      },
  };
  /**
   * dot-task
   * jsPsych plugin for displaying a stimulus and getting a button response
   * @author Josh de Leeuw
   * @see {@link https://www.jspsych.org/plugins/jspsych-dot-task/ dot-task plugin documentation on jspsych.org}
   */
  class DotTaskPlugin {
      constructor(jsPsych) {
          this.jsPsych = jsPsych;
      }
      trial(display_element, trial) {
          //params
          var dot_positions = trial.dot_positions;
          var rect_width = trial.rect_dims[0]
          var rect_height = trial.rect_dims[1]
          var dot_rad = trial.dot_radius
          var static_color = "rgb(255,100,100)"
          var feedback_dot_rad = dot_rad + 2
          var feedback_color = "rgb(255,0,0)"

          // display stimulus
          var html = '<div id="jspsych-dot-task-stimulus">' + trial.stimulus + "</div>";
          //display buttons
          var buttons = [];
          if (Array.isArray(trial.button_html)) {
              if (trial.button_html.length == trial.choices.length) {
                  buttons = trial.button_html;
              }
              else {
                  console.error("Error in dot-task plugin. The length of the button_html array does not equal the length of the choices array");
              }
          }
          else {
              for (var i = 0; i < trial.choices.length; i++) {
                  buttons.push(trial.button_html);
              }
          }
          html += '<div id="jspsych-dot-task-btngroup">';
          for (var i = 0; i < trial.choices.length; i++) {
              var str = buttons[i].replace(/%choice%/g, trial.choices[i]);
              html +=
                  '<div class="jspsych-dot-task-button" style="display: inline-block; margin:' +
                      trial.margin_vertical +
                      " " +
                      trial.margin_horizontal +
                      '" id="jspsych-dot-task-button-' +
                      i +
                      '" data-choice="' +
                      i +
                      '">' +
                      str +
                      "</div>";
          }
          html += "</div>";
          //show prompt if there is one
          if (trial.prompt !== null) {
              html += trial.prompt;
          }
          display_element.innerHTML = html;
          // start time
          var start_time = performance.now();
          var click_x = [];  
          var click_y = [];  
          var dot_idx = 0; 
          var rts = []
          var end_time = null;
          var ignore_click = false;
          // add event listeners to buttons
          for (var i = 0; i < trial.choices.length; i++) {
              display_element
                  .querySelector("#jspsych-dot-task-button-" + i)
                  .addEventListener("click", (e) => {
                  if(ignore_click) {
                      return;
                  }

                  //record click pos
                  var btn_el = e.currentTarget;
                  //this gives position of button relative to screen you're viewing. So, if scrolled down, pos y will be negative
                  var button_pos = btn_el.getBoundingClientRect();               
                  //how far right along button
                  click_x.push(e.pageX - (button_pos.x + window.scrollX));
                  //how far down from top of button
                  click_y.push(rect_height - (e.pageY - (button_pos.y + window.scrollY)));
                  
                  //iterate dot idx to display next dot
                  dot_idx = dot_idx + 1

                  //record rt
                  end_time = performance.now();
                  rts.push(end_time - start_time);

                  //now briefly display guess/feedback
                  update_html1()
                  //and then next dot
                  update_html2()
              });
          }
          // store response
          var response = {
              rt: null,
              button: null,
          };

          //update html to show guess and true dot feedback
          function update_html1() {
            //don't let user give another response until html has updated
            ignore_click=true;
            //add in black dot at click position
            var response_dot_html = '<div id="temp-dot-1" style="position:absolute; bottom:' + (click_y[click_y.length-1]-dot_rad) + 'px; left:' + (click_x[click_x.length-1]-dot_rad) + 'px; width:' + (dot_rad * 2) + 'px; height:'+ (dot_rad * 2) + 'px;-webkit-border-radius: ' + dot_rad + 'px;-moz-border-radius:' + dot_rad + 'px;border-radius:' + dot_rad + 'px;background: black;"></div>';
            var true_dot_html = '<div id="temp-dot-2" style="position:absolute; bottom:' + (dot_positions[1][dot_idx]-feedback_dot_rad) + 'px; left:' + (dot_positions[0][dot_idx]-feedback_dot_rad) + 'px; width:' + (feedback_dot_rad * 2) + 'px; height:'+ (feedback_dot_rad * 2) + 'px;-webkit-border-radius: ' + feedback_dot_rad + 'px;-moz-border-radius:' + feedback_dot_rad + 'px;border-radius:' + feedback_dot_rad + 'px;background: ' + feedback_color + ';"></div>';
            
            document.getElementById("target").insertAdjacentHTML('beforeEnd', response_dot_html); 
            
            //wait 500 ms before showing true dot
            setTimeout(() => {
                document.getElementById("target").insertAdjacentHTML('beforeEnd', true_dot_html);
                //start time after true dot becomes visible
                //so all response times after first will be at least 1000 ms, while button is inactive
                start_time = performance.now();
            }, 500);

          };

          //update html to get rid of guess and feedback dots and show dots so far in red
          function update_html2() {
            var feedback_duration = 1500
            if(dot_idx == dot_positions[0].length-1) {
                feedback_duration = 2000
            }
            setTimeout(() => {
                document.getElementById("temp-dot-1").remove();
                document.getElementById("temp-dot-2").remove();
                ignore_click=false;

                //add in last dot in red
                var dot_html = '<div id="dot-' + dot_idx +  '" style="position:absolute; bottom:' + (dot_positions[1][dot_idx]-dot_rad) + 'px; left:' + (dot_positions[0][dot_idx]-dot_rad) + 'px; width:' + (dot_rad * 2) + 'px; height:'+ (dot_rad * 2) + 'px;-webkit-border-radius: ' + dot_rad + 'px;-moz-border-radius:' + dot_rad + 'px;border-radius:' + dot_rad + 'px;background: ' + static_color + ';"></div>';
                document.getElementById("target").insertAdjacentHTML('beforeEnd', dot_html);
                
                //if that was the last dot to show, end
                if (dot_idx == dot_positions[0].length-1) {
                    end_trial();
                }
                //if they seem to have gotten the pattern, also end

                if (have_they_got_it(click_x, click_y, dot_positions[0], dot_positions[1])) {
                    end_trial();
                }

            }, feedback_duration);  
          };

          //does this participant seem to have gotten the pattern?
          //some can change over time. Should we do at least 10 dots?
          //and then, starting with the 11th, if the last 3 have been extremely close (idk brah)
          //can also do something smarter - like based on ave distance between dots so far
          function have_they_got_it(res_x, res_y, true_x, true_y) {
            //note that res_x[i] corresponds to true_x[i+1] bc we are guessing one behind
            if(res_x.length < 13) {
                return false;
            }
            //check past 4 (earliest would be 10-13th dot correct)
            for(i=res_x.length - 1; i>res_x.length - 5; i=i-1) {
                //check distance between response and correct not too large
                if(Math.hypot(res_x[i] - true_x[i+1], res_y[i] - true_y[i+1]) > 4) {
                    return false;
                }
            }
            return true;
          };
          // function to end trial when it is time
          const end_trial = () => {
              // kill any remaining setTimeout handlers
              this.jsPsych.pluginAPI.clearAllTimeouts();
              // gather the data to store for the trial
              var trial_data = {
                  rt: rts,
                  response_x: click_x,
                  response_y: click_y,
              };
              // clear the display
              display_element.innerHTML = "";
              // move on to the next trial
              this.jsPsych.finishTrial(trial_data);
          };
          /*
          // function to handle responses by the subject
          function after_response(choice) {
              // measure rt
              var end_time = performance.now();
              var rt = Math.round(end_time - start_time);
              response.button = parseInt(choice);
              response.rt = rt;
              // after a valid response, the stimulus will have the CSS class 'responded'
              // which can be used to provide visual feedback that a response was recorded
              display_element.querySelector("#jspsych-dot-task-stimulus").className +=
                  " responded";
              // disable all the buttons after a response
              var btns = document.querySelectorAll(".jspsych-dot-task-button button");
              for (var i = 0; i < btns.length; i++) {
                  //btns[i].removeEventListener('click');
                  btns[i].setAttribute("disabled", "disabled");
              }
              if (trial.response_ends_trial) {
                  end_trial();
              }
          }
          */
          // hide image if timing is set
          if (trial.stimulus_duration !== null) {
              this.jsPsych.pluginAPI.setTimeout(() => {
                  display_element.querySelector("#jspsych-dot-task-stimulus").style.visibility = "hidden";
              }, trial.stimulus_duration);
          }
          // end trial if time limit is set
          if (trial.trial_duration !== null) {
              this.jsPsych.pluginAPI.setTimeout(end_trial, trial.trial_duration);
          }
      }
      simulate(trial, simulation_mode, simulation_options, load_callback) {
          if (simulation_mode == "data-only") {
              load_callback();
              this.simulate_data_only(trial, simulation_options);
          }
          if (simulation_mode == "visual") {
              this.simulate_visual(trial, simulation_options, load_callback);
          }
      }
      create_simulation_data(trial, simulation_options) {
          const default_data = {
              stimulus: trial.stimulus,
              rt: this.jsPsych.randomization.sampleExGaussian(500, 50, 1 / 150, true),
              response: this.jsPsych.randomization.randomInt(0, trial.choices.length - 1),
          };
          const data = this.jsPsych.pluginAPI.mergeSimulationData(default_data, simulation_options);
          this.jsPsych.pluginAPI.ensureSimulationDataConsistency(trial, data);
          return data;
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
              this.jsPsych.pluginAPI.clickTarget(display_element.querySelector(`div[data-choice="${data.response}"] button`), data.rt);
          }
      }
  }
  DotTaskPlugin.info = info;

  return DotTaskPlugin;

})(jsPsychModule);
