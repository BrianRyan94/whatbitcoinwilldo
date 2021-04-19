import React from "react";
import SharedStyles from "./SharedStyles";
import Button from "@material-ui/core/Button";
import Box from "@material-ui/core/Box";
import Typography from "@material-ui/core/Typography";

const Footer = () => {
  const shared_styles = SharedStyles();
  return (
    <Box bgcolor="primary.main" boxShadow={2} className={shared_styles.Footer}>
      <Button color="secondary" href={`mailto:whatbitcoinisdoing@gmail.com`}>
        <Typography>Contact | Email: whatbitcoinisdoing@gmail.com</Typography>
      </Button>
    </Box>
  );
};

export default Footer;
