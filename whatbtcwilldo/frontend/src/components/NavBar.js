import React from "react";
import { AppBar } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import SharedStyles from "./SharedStyles";
import Typography from "@material-ui/core/Typography";

const compStyles = makeStyles({
  nav_logo: {
    marginLeft: "30px",
  },
});

const NavBar = () => {
  const shared_styles = SharedStyles();
  const comp_styles = compStyles();

  return (
    <AppBar position="static" className={`${shared_styles.primary_background}`}>
      <Typography
        variant="h6"
        className={`${shared_styles.header_text} ${comp_styles.nav_logo}`}
      >
        WhatBitcoinWilldo
      </Typography>
    </AppBar>
  );
};

export default NavBar;
