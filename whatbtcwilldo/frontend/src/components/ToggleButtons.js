import { makeStyles } from "@material-ui/core";
import ToggleButton from "@material-ui/lab/ToggleButton";
import ToggleButtonGroup from "@material-ui/lab/ToggleButtonGroup";
import React, { useState } from "react";
import SharedStyles from "./SharedStyles";

const toggleStyle = makeStyles((theme) => ({
  root: {
    color: theme.palette["primary"].main,
  },
}));

const toggleButtons = ({ options, defaultOption, callBack }) => {
  const toggle_style = toggleStyle();
  const [chosen_val, setChosen_val] = useState(defaultOption);

  const handleChange = (event, newValue) => {
    setChosen_val(newValue);
    callBack(newValue);
  };

  const shared_style = SharedStyles();
  return (
    <div className={shared_style.centered_within}>
      <ToggleButtonGroup value={chosen_val} exclusive onChange={handleChange}>
        {options.map((option) => {
          return (
            <ToggleButton classes={toggle_style} value={option}>
              {option}
            </ToggleButton>
          );
        })}
      </ToggleButtonGroup>
    </div>
  );
};

export default toggleButtons;
