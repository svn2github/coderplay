/**
 * 
 */
package src;

import java.util.ArrayList;

/**
 * @author ywang
 * 
 */
public class MSMain {

	private static int nsize = 10;
	private static boolean isConstrained = false;
	private static int prow = 0, pcol = 0;
	private static ArrayList<int[]> closed = new ArrayList<int[]>();
	private static long matrix;

	/**
	 * Parse the command line arguments and set the related variables.
	 * 
	 * @param args
	 * @return 1 for success; 0 for error/failure.
	 */
	private static int parseOpt(String[] args) {
		int argidx = 0;
		while (argidx < args.length) {
			if (args[argidx].equals("-n")) {
				try {
					argidx += 1;
					nsize = Integer.parseInt(args[argidx]);
				} catch (NumberFormatException e1) {
					System.out.println("Incorrect argument following -n.");
					return 0;
				}
			} else if (args[argidx].equals("-c")) {
				isConstrained = true;
			} else if (args[argidx].equals("-p")) {
				try {
					argidx += 1;
					prow = Integer.parseInt(args[argidx]);
					argidx += 1;
					pcol = Integer.parseInt(args[argidx]);
				} catch (NumberFormatException e2) {
					System.out.println("Incorrect argument following -p.");
					return 0;
				}
			} else {
				System.out.println("Unknown option: " + args[argidx]);
				return 0;
			}
			argidx += 1;
		}
		return 1;
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		
		
		if (parseOpt(args) == 0)
			System.exit(1);
		
		int ii, jj;
		int lsidx, rsidx; // left/right row index
		int leidx, reidx; // left/right element index

		
		System.out.println("-n " + nsize);
		System.out.println("-c " + isConstrained);
		System.out.println("-p " + prow + " " + pcol);

		// Setup common variables, e.g. the initial matrix, the goalsum
		MSMatrix mat = new MSMatrix(nsize, isConstrained, prow, pcol);
		mat.print();
		mat.printsums();
		Integer [] idxsort = mat.getIdxSortSums();
		for (Integer idx: idxsort) {
			System.out.print(" "+idx);
		}
		System.out.println();

		// calculate the sums and stats of the initial matrix

		// main loop of the search
		do {
			
			idxsort = mat.getIdxSortSums();

			// Generate and enqueue a new matrix
			if (mat.getDistance() > mat.getUpbound0()) { // Fast descent to low state space
				for (ii=0;ii<nsize+nsize+2;ii++) {
					
					for (jj=0;jj<nsize+nsize;jj++) {
					
					}
				}
				
				
				
			} else {
				// Perform either paired swap or simple swap in low state space

			}

			// update the sums and stats for the new matrix based on the old
			// matrix data

		} while (false); // while (mat.getDistance() != 0);

		// end here

	}

}
