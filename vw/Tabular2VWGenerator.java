package vw;

import java.io.*;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Collectors;

/**
 * This class is a util to transform a standard tabular dataset for binary classification
 * into a Vowpal Wabbit format.
 *
 * Created by padjiman on 26/10/2017.
 */
public class Tabular2VWGenerator{

    /**
     *
     * Core function that is transforming a tabular dataset into its VW format. For more details.
     * Input file must contain an header with feature names. See this post for more details:
     * http://www.philippeadjiman.com/blog/2018/04/02/deep-dive-into-logistic-regression-part-3
     *
     * @param workingDir the working directory where all inputs are and all outputs are generated
     * @param inputFile the name of the file were there is the raw tabular dataset
     * @param outputFile name of the generated output file containing the dataset in VW Format
     * @param featureIndexOutputFile name of the generated output file containing the mapping between short feature
     *                               names and original feature name (see blog post for examples)
     * @param numericalFeatures set of feature names (as they appear in the header of inputFile) that are numeric
     * @param categoricalFeatures set of feature names (as they appear in the header of inputFile) that are categorical
     * @param targetLabel the name of the feature (as it appears in the header) that contains the target variable
     * @param sep the separator used in input file (most often either ; or , or \t)
     * @param positiveLabel the positive value of the target variable used in the input file (e.g. 1 or yes or true)
     * @param separateNamespace if you want the output file of the dataset in VW format to use two separate namespaces
     *                          (one for numerical features and one for categorical features)
     * @throws IOException
     * @throws ParseException
     */
    public void tabular2VWGenerator(String workingDir, String inputFile, String outputFile, String featureIndexOutputFile, final List<String> numericalFeatures, final List<String> categoricalFeatures,
                                    final String targetLabel, final String sep, final String positiveLabel, final boolean separateNamespace ) throws IOException, ParseException {

        BufferedReader reader =
                new BufferedReader(new FileReader(workingDir+inputFile));

        FileWriter fileWriter = new FileWriter(workingDir+outputFile);
        PrintWriter printWriter = new PrintWriter(fileWriter);
        FileWriter featureIndexWriter = new FileWriter(workingDir+featureIndexOutputFile);
        PrintWriter featureIndexPrintWriter = new PrintWriter(featureIndexWriter);

        String dataRow = reader.readLine(); // header
        final String[] headerSplit = dataRow.split(sep);
        final HashMap<String, Integer> featureIndexMap = new HashMap<>();
        for(int i=0; i< headerSplit.length; i++){
            String columnName = headerSplit[i].replace("\"", "").trim(); // Remove quotes and spaces
            featureIndexMap.put(columnName, i);
            featureIndexPrintWriter.println(String.format("F%d: %s", i, columnName));
        }

        final ArrayList<Integer> numericalFeaturesIndexes = buildFeatureIndexes(numericalFeatures, featureIndexMap);
        final ArrayList<Integer> categoricalFeaturesIndexes = buildFeatureIndexes(categoricalFeatures, featureIndexMap);
        final Integer labelIndex = featureIndexMap.get(targetLabel);
        if (labelIndex == null) {
        throw new IllegalArgumentException("Target label '" + targetLabel + "' not found in the dataset header.");
        }

        int pos = 0;
        int neg =0;
        dataRow = reader.readLine();
        while (dataRow != null){
            String[] dataArray = dataRow.split(sep);
            String label = dataArray[labelIndex];
            if(label.equals(positiveLabel)){
                pos++;
                label="1";
            }
            else{
                neg++;
                label="-1";
            }


            ArrayList<String> int_features =
                    numericalFeaturesIndexes.stream().
                            filter(i -> !dataArray[i].trim().equals("")).
                            map(i -> String.format("F%d:%s", i, dataArray[i])).
                            collect(Collectors.toCollection(ArrayList::new));

            String int_features_string;
            int_features_string = String.join(" ",int_features);

            ArrayList<String> cat_features =
                    categoricalFeaturesIndexes.stream().
                    filter(i -> !dataArray[i].trim().equals("")).
                    map(i -> String.format("F%d=%s", i, dataArray[i])).
                    collect(Collectors.toCollection(ArrayList::new));

            String cat_features_string;
            cat_features_string = String.join(" ",cat_features);

            if (separateNamespace) {
                printWriter.println(String.format("%s |i %s |c %s", label, int_features_string, cat_features_string));
            }else{
                printWriter.println(String.format("%s |f %s %s", label, int_features_string, cat_features_string));
            }

            dataRow = reader.readLine();
        }
        printWriter.close();
        featureIndexWriter.close();

        System.out.println("Number of negative examples: "+neg);
        System.out.println("Number of positive examples: "+pos);
        System.out.println(String.format("Generated files in %s: %s and %s",
                workingDir, outputFile, featureIndexOutputFile));

    }

    private static ArrayList<Integer> buildFeatureIndexes(List<String> features, HashMap<String, Integer> featureIndexMap) {
        final ArrayList<Integer> featuresIndexes = new ArrayList<>();
        for(String f : features){
            final Integer idx = featureIndexMap.get(f);
            if( idx != null ){
                featuresIndexes.add(idx);
            }
        }

        return featuresIndexes;
    }

    public static void main(String[] args) throws IOException, ParseException {
        final Tabular2VWGenerator tabular2VWGenerator = new Tabular2VWGenerator();
        tabular2VWGenerator.generateBankTrainingSet();
//        tabular2VWGenerator.generateDonationTrainingSet();
    }

    /**
     * Call the tabular2VWGenerator on the dataset found in https://archive.ics.uci.edu/ml/datasets/Bank+Marketing
     *
     * @throws IOException
     * @throws ParseException
     */
    public void generateBankTrainingSet() throws IOException, ParseException {
        final String workingDir = "data/";
        final List<String> numericalFeatures = Arrays.asList(new String[]{"age", "balance", "duration", "campaign", "pdays", "previous"});
        final List<String> categoricalFeatures = Arrays.asList(new String[]{"job", "marital", "education", "default", "housing", "contact", "day", "month", "poutcome"});
        final String targetLabel = "y";
        final String sep = ";";
        String positiveLabel = "\"yes\"";
        tabular2VWGenerator(workingDir,"bank-full.csv",
                "train.vw", "featuresIndexes.txt",  numericalFeatures, categoricalFeatures, targetLabel, sep, positiveLabel,true);

    }

    /**
     * Call the tabular2VWGenerator on the dataset found in https://archive.ics.uci.edu/ml/datasets/KDD+Cup+1998+Data
     *
     * @throws IOException
     * @throws ParseException
     */
    public void generateDonationTrainingSet() throws IOException, ParseException {
        final String workingDir = "data/output";
        //ALL FEATURES:
        //        final List<String> numericalFeatures = Arrays.asList(new String[]{"AGE","NUMCHLD","INCOME","WEALTH1","HIT","MBCRAFT","MBGARDEN","MBBOOKS","MBCOLECT","MAGFAML","MAGFEM","MAGMALE","PUBGARDN","PUBCULIN","PUBHLTH","PUBDOITY","PUBNEWFN","PUBPHOTO","PUBOPP","DATASRCE","MALEMILI","MALEVET","VIETVETS","WWIIVETS","LOCALGOV","STATEGOV","FEDGOV","SOLP3","SOLIH","WEALTH2","POP901","POP902","POP903","POP90C1","POP90C2","POP90C3","POP90C4","POP90C5","ETH1","ETH2","ETH3","ETH4","ETH5","ETH6","ETH7","ETH8","ETH9","ETH10","ETH11","ETH12","ETH13","ETH14","ETH15","ETH16","AGE901","AGE902","AGE903","AGE904","AGE905","AGE906","AGE907","CHIL1","CHIL2","CHIL3","AGEC1","AGEC2","AGEC3","AGEC4","AGEC5","AGEC6","AGEC7","CHILC1","CHILC2","CHILC3","CHILC4","CHILC5","HHAGE1","HHAGE2","HHAGE3","HHN1","HHN2","HHN3","HHN4","HHN5","HHN6","MARR1","MARR2","MARR3","MARR4","HHP1","HHP2","DW1","DW2","DW3","DW4","DW5","DW6","DW7","DW8","DW9","HV1","HV2","HV3","HV4","HU1","HU2","HU3","HU4","HU5","HHD1","HHD2","HHD3","HHD4","HHD5","HHD6","HHD7","HHD8","HHD9","HHD10","HHD11","HHD12","ETHC1","ETHC2","ETHC3","ETHC4","ETHC5","ETHC6","HVP1","HVP2","HVP3","HVP4","HVP5","HVP6","HUR1","HUR2","RHP1","RHP2","RHP3","RHP4","HUPA1","HUPA2","HUPA3","HUPA4","HUPA5","HUPA6","HUPA7","RP1","RP2","RP3","RP4","MSA","ADI","DMA","IC1","IC2","IC3","IC4","IC5","IC6","IC7","IC8","IC9","IC10","IC11","IC12","IC13","IC14","IC15","IC16","IC17","IC18","IC19","IC20","IC21","IC22","IC23","HHAS1","HHAS2","HHAS3","HHAS4","MC1","MC2","MC3","TPE1","TPE2","TPE3","TPE4","TPE5","TPE6","TPE7","TPE8","TPE9","PEC1","PEC2","TPE10","TPE11","TPE12","TPE13","LFC1","LFC2","LFC3","LFC4","LFC5","LFC6","LFC7","LFC8","LFC9","LFC10","OCC1","OCC2","OCC3","OCC4","OCC5","OCC6","OCC7","OCC8","OCC9","OCC10","OCC11","OCC12","OCC13","EIC1","EIC2","EIC3","EIC4","EIC5","EIC6","EIC7","EIC8","EIC9","EIC10","EIC11","EIC12","EIC13","EIC14","EIC15","EIC16","OEDC1","OEDC2","OEDC3","OEDC4","OEDC5","OEDC6","OEDC7","EC1","EC2","EC3","EC4","EC5","EC6","EC7","EC8","SEC1","SEC2","SEC3","SEC4","SEC5","AFC1","AFC2","AFC3","AFC4","AFC5","AFC6","VC1","VC2","VC3","VC4","ANC1","ANC2","ANC3","ANC4","ANC5","ANC6","ANC7","ANC8","ANC9","ANC10","ANC11","ANC12","ANC13","ANC14","ANC15","POBC1","POBC2","LSC1","LSC2","LSC3","LSC4","VOC1","VOC2","VOC3","HC1","HC2","HC3","HC4","HC5","HC6","HC7","HC8","HC9","HC10","HC11","HC12","HC13","HC14","HC15","HC16","HC17","HC18","HC19","HC20","HC21","MHUC1","MHUC2","AC1","AC2","CARDPROM","MAXADATE","NUMPROM","CARDPM12","NUMPRM12","RDATE_3","RDATE_4","RDATE_5","RDATE_6","RDATE_7","RDATE_8","RDATE_9","RDATE_10","RDATE_11","RDATE_12","RDATE_13","RDATE_14","RDATE_15","RDATE_16","RDATE_17","RDATE_18","RDATE_19","RDATE_20","RDATE_21","RDATE_22","RDATE_23","RDATE_24","RAMNT_3","RAMNT_4","RAMNT_5","RAMNT_6","RAMNT_7","RAMNT_8","RAMNT_9","RAMNT_10","RAMNT_11","RAMNT_12","RAMNT_13","RAMNT_14","RAMNT_15","RAMNT_16","RAMNT_17","RAMNT_18","RAMNT_19","RAMNT_20","RAMNT_21","RAMNT_22","RAMNT_23","RAMNT_24","RAMNTALL","NGIFTALL","CARDGIFT","MINRAMNT","MINRDATE","MAXRAMNT","MAXRDATE","LASTGIFT","LASTDATE","FISTDATE","NEXTDATE","TIMELAG","AVGGIFT"});
        //        final List<String> categoricalFeatures = Arrays.asList(new String[]{"OSOURCE","TCODE","STATE","ZIP","MAILCODE","PVASTATE","DOB","NOEXCH","RECINHSE","RECP3","RECPGVG","RECSWEEP","MDMAUD","DOMAIN","CLUSTER","AGEFLAG","HOMEOWNR","CHILD03","CHILD07","CHILD12","CHILD18","GENDER","MAJOR","GEOCODE","COLLECT1","VETERANS","BIBLE","CATLG","HOMEE","PETS","CDPLAY","STEREO","PCOWNERS","PHOTO","CRAFTS","FISHER","GARDENIN","BOATS","WALKER","KIDSTUFF","CARDS","PLATES","LIFESRC","PEPSTRFL","ADATE_2","ADATE_3","ADATE_4","ADATE_5","ADATE_6","ADATE_7","ADATE_8","ADATE_9","ADATE_10","ADATE_11","ADATE_12","ADATE_13","ADATE_14","ADATE_15","ADATE_16","ADATE_17","ADATE_18","ADATE_19","ADATE_20","ADATE_21","ADATE_22","ADATE_23","ADATE_24","RFA_2","RFA_3","RFA_4","RFA_5","RFA_6","RFA_7","RFA_8","RFA_9","RFA_10","RFA_11","RFA_12","RFA_13","RFA_14","RFA_15","RFA_16","RFA_17","RFA_18","RFA_19","RFA_20","RFA_21","RFA_22","RFA_23","RFA_24","HPHONE_D","RFA_2R","RFA_2F","RFA_2A","MDMAUD_R","MDMAUD_F","MDMAUD_A","CLUSTER2","GEOCODE2"});

        //Some Selected Features:
        final List<String> numericalFeatures = Arrays.asList(new String[]{"AGE","NUMCHLD","INCOME","WEALTH1","HIT","MBCRAFT","MBGARDEN","PUBHLTH","PUBDOITY","PUBNEWFN","PUBPHOTO","PUBOPP","RAMNTALL","NGIFTALL","CARDGIFT","MINRAMNT","MINRDATE","MAXRAMNT","MAXRDATE","LASTGIFT","LASTDATE","FISTDATE","NEXTDATE","TIMELAG","AVGGIFT"});
        final List<String> categoricalFeatures = Arrays.asList(new String[]{"OSOURCE","TCODE","STATE","ZIP","MAILCODE","PVASTATE","DOB","NOEXCH","RECINHSE","GEOCODE2"});
        final String targetLabel = "TARGET_B";
        final String sep = ",";
        String positiveLabel = "1";
        tabular2VWGenerator(workingDir,"cup98LRN.csv",
                "train_less_features.vw",
                "featuresIndexes.txt", numericalFeatures, categoricalFeatures, targetLabel, sep, positiveLabel, true);

    }
    
}