/**
 * 
 */

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
		int ldiff, rdiff;
		int lgval, rgval;
		int lgidx, rgidx;

		int nsize2 = nsize + nsize;
		int nsums = nsize2 + 2;

		System.out.println("-n " + nsize);
		System.out.println("-c " + isConstrained);
		System.out.println("-p " + prow + " " + pcol);

		// Setup common variables, e.g. the initial matrix, the goalsum
		MSMatrix mat = new MSMatrix(nsize, isConstrained, prow, pcol);
		System.out.println(mat.getUpbound0());
		mat.print();
		mat.printsums();
		System.out.println(mat.getGoalsum());
		System.out.println(mat.getDistance());
		Integer[] idxsort = mat.getIdxSortSums();
		int nuniquesums;
		boolean[] fcons = mat.getFcons();
		Integer[] idxforsum1_sort;
		Integer[] idxforsum2_sort;

		for (Integer idx : idxsort) {
			System.out.print(" " + idx);
		}
		System.out.println();

		// calculate the sums and stats of the initial matrix

		boolean findit, candidateSwap;
		int[] matrixBest;
		long distanceBest;
		int[] sumsBest;
		int symetricBest;
		long distanceCurrent;
		int symetricCurrent;
		Integer[] idxsortNew;
		int temp;
		temp = 50;

		// main loop of the search
		do {

			idxsort = mat.getIdxSortSums();
			distanceCurrent = mat.getDistance();
			symetricCurrent = mat.countSymetric(idxsort);

			// Generate and enqueue a new matrix
			if (mat.getDistance() > mat.getUpbound0()) { // Fast descent to low
															// state space
				findit = false;
				for (ii = 0; ii < nsums; ii++) {

					// The sums to work on
					lsidx = ii / 2;
					rsidx = nsums - 1 - (ii / 2 + ii % 2);
					System.out.println(lsidx + ", " + rsidx);
					if (lsidx >= rsidx) {
						System.out.println("Error!");
						mat.print();
						mat.printsums();
						System.out.println(mat.getDistance());
						System.exit(1);
					}

					idxforsum1_sort = mat
							.getSortedIndexOfSingleSumElements(idxsort[lsidx]);
					idxforsum2_sort = mat
							.getSortedIndexOfSingleSumElements(idxsort[rsidx]);

					for (jj = 0; jj < nsize2; jj++) {
						leidx = jj / 2;
						reidx = nsize2 - 1 - (jj / 2 + jj % 2) - nsize;

						if (leidx >= nsize || reidx < 0)
							break;

						if (mat.isIndexConstrained(idxforsum1_sort[leidx]
								.intValue())
								|| mat.isIndexConstrained(idxforsum2_sort[reidx]
										.intValue())) {
							continue;
						}

						// Try the swap
						mat.update(idxforsum1_sort[leidx].intValue(),
								idxforsum2_sort[reidx].intValue());

						// Test the swap
						if (mat.verifyUpdateSimple()
								&& !closed.contains(mat.getMatrix())) {
							findit = true;
							System.out.println(idxforsum1_sort[leidx] + ":: "
									+ idxforsum2_sort[reidx]);
							break;
						} else {
							mat.revertUpdate();
						}
					}
					if (findit)
						break;
				}

			} else {

				matrixBest = null;
				symetricBest = -1;
				distanceBest = Long.MAX_VALUE;
				sumsBest = null;

				lsidx = idxsort[0];
				rsidx = idxsort[idxsort.length - 1];
				idxforsum1_sort = mat.getSortedIndexOfSingleSumElements(lsidx);
				idxforsum2_sort = mat.getSortedIndexOfSingleSumElements(rsidx);

				// Perform either paired swap or simple swap in low state space
				for (ii = 0; ii < nsize2; ii++) {
					leidx = ii / 2;
					reidx = nsize2 - 1 - (ii / 2 + ii % 2) - nsize;

					if (leidx >= nsize || reidx < 0) {
						break;
					}

					// Constrained
					if (mat.isIndexConstrained(idxforsum1_sort[leidx]
							.intValue())
							|| mat.isIndexConstrained(idxforsum2_sort[reidx]
									.intValue())) {
						continue;
					}

					ldiff = mat.getSums()[lsidx] - mat.getGoalsum();
					rdiff = mat.getSums()[rsidx] - mat.getGoalsum();
					
					lgval = mat.getMatrix()[idxforsum1_sort[leidx].intValue()] - ldiff;
					rgval = mat.getMatrix()[idxforsum2_sort[reidx].intValue()] - rdiff;

					lgidx = mat.getIndexForElement(lgval);
					rgidx = mat.getIndexForElement(rgval);

					
					// System.out.println(lgval+", "+rgval+"   ->"+lgidx+"; "+rgidx+ "   -> "+leidx+", "+reidx);
					
					candidateSwap = true;
					if (lgidx != -1 && rgidx != -1) {
						for (jj = 0; jj < nsize; jj++) {
							if (lgidx == idxforsum1_sort[jj]
									|| lgidx == idxforsum2_sort[jj]
									|| rgidx == idxforsum1_sort[jj]
									|| rgidx == idxforsum2_sort[jj]) {

								candidateSwap = false;
								break;
							}
						}
					} else {
						candidateSwap = false;
					}

					if (candidateSwap) {
						// System.out.println("paired swap");
						// try paired swap
						mat.updatePairedSwap(idxforsum1_sort[leidx].intValue(),
								lgidx, idxforsum1_sort[leidx].intValue(), rgidx);
					} else {
						//System.out.println("simple swap");
						// try simple swap
						mat.update(idxforsum1_sort[leidx].intValue(),
								idxforsum2_sort[reidx].intValue());
					}

					if (!closed.contains(mat.getMatrix())) {
						if (matrixBest == null) {
							matrixBest = mat.getMatrix().clone();
							distanceBest = mat.getDistance();
							sumsBest = mat.getSums().clone();
							symetricBest = mat.countSymetric(idxsort);
						} else {
							idxsortNew = mat.getIdxSortSums();
							if (mat.countSymetric(idxsortNew) > symetricBest) {
								matrixBest = mat.getMatrix().clone();
								distanceBest = mat.getDistance();
								sumsBest = mat.getSums().clone();
								symetricBest = mat.countSymetric(idxsortNew);
							} else {
								if (mat.getDistance() < distanceBest) {
									matrixBest = mat.getMatrix().clone();
									distanceBest = mat.getDistance();
									sumsBest = mat.getSums().clone();
									symetricBest = mat
											.countSymetric(idxsortNew);
								}
							}
						}
					}

					mat.revertUpdate();

				}

				if (matrixBest != null) {
					mat.setMatrix(matrixBest);
					mat.setDistance(distanceBest);
					mat.setSums(sumsBest);
				} else {
					System.out.println("Error 3");
					System.exit(1);
				}

			}

			closed.add(mat.getMatrix().clone());

			// update the sums and stats for the new matrix based on the old
			// matrix data
			temp--;

			mat.print();
			mat.printsums();
			System.out.println(mat.getDistance());
			System.out.println("close size "+closed.size());
			System.out.println(mat.getMatrix());
			System.out.println("temp = " + temp);
			int [] test1 = {1, 2, 3, 4};
			int [] test2 = {1,2,3,4};
			System.out.println(test1.equals(test2));
			

		} while (mat.getDistance() != 0); // while (mat.getDistance() != 0);

		// end here

		mat.print();
		mat.printsums();
		System.out.println(mat.getDistance());
		System.out.println("temp = " + temp);

	}

}
