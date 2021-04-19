import React from "react";
import SharedStyles from "./SharedStyles";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import { makeStyles } from "@material-ui/core/styles";
import { useMediaQuery } from "react-responsive";

const compStyles = makeStyles({
  descriptionUnitLabel: {
    marginRight: "3px",
    color: "darkslategray",
  },

  descriptionUnitValue: {
    marginRight: "7px",
  },

  positiveSentiment: {
    color: "green",
  },

  negativeSentiment: {
    color: "red",
  },

  verticalMargins: {
    marginTop: "10px",
    margingBottom: "5px",
  },

  infoArrayObjectSmallest: {
    flexBasis: "12%",
  },

  infoArrayObjectMedium: {
    flexBasis: "33%",
  },

  infoArrayObjectLargest: {
    flexBasis: "45%",
  },
});

const InfoCard = ({ infoArray }) => {
  const comp_styles = compStyles();
  const shared_styles = SharedStyles();

  //if it is a narrow screen
  const narrow_screen = useMediaQuery({ maxWidth: 380 });
  //if it is big enough to have 2 on each row
  const row_display = useMediaQuery({ minWidth: 1000 });
  //if it is an extra wide screen
  const wide_screen = useMediaQuery({ minWidth: 1300 });
  //is a large column
  const large_column = useMediaQuery({ minWidth: 700 });

  const isLargest =
    wide_screen | ((row_display == false) & (large_column == true));

  const isSmallest = narrow_screen;

  return (
    <>
      <Card className={comp_styles.verticalMargins}>
        <CardContent
          className={`${shared_styles.secondary_background} ${shared_styles.flexRow} ${shared_styles.RowWrap} ${shared_styles.spaceBetween}`}
        >
          {infoArray
            ? infoArray.map((infoUnit) => {
                return (
                  <div
                    className={`${shared_styles.flexRow} ${
                      isLargest
                        ? comp_styles.infoArrayObjectSmallest
                        : isSmallest
                        ? comp_styles.infoArrayObjectLargest
                        : comp_styles.infoArrayObjectMedium
                    }`}
                  >
                    <Typography className={comp_styles.descriptionUnitLabel}>
                      {infoUnit[0]}:
                    </Typography>
                    <Typography
                      className={`${comp_styles.descriptionUnitValue} ${
                        infoUnit[2] == "positive"
                          ? comp_styles.positiveSentiment
                          : comp_styles.negativeSentiment
                      }`}
                    >
                      {infoUnit[1]}
                    </Typography>
                  </div>
                );
              })
            : null}
        </CardContent>
      </Card>
    </>
  );
};

export default InfoCard;
