/**
 * 
 */
package src;

import java.nio.IntBuffer;
import java.util.Arrays;
import java.util.Comparator;

/**
 * @author ywang
 * 
 */
public class MSMatrix {

	private int[] matrix;

	private int nsize;
	private int nsize2;
	private int nelements;
	private int goalsum;
	private long distance;
	private int[] sums;
	private Integer[] idxs;
	private boolean[] fcons; // the constraint flag matrix
	private int[][] idxforsum;
	private int[] idxSumChange = new int[4];
	private long upbound0;

	private int[] matrixOld;
	private long distanceOld;
	private int[] sumsOld;

	public MSMatrix(int nsize, boolean isConstrained, int prow, int pcol) {

		int ii, jj;

		this.nsize = nsize;
		nsize2 = nsize + nsize;
		nelements = nsize * nsize;
		matrix = new int[nelements];
		sums = new int[nsize2 + 2];
		idxs = new Integer[nsize2 + 2];
		goalsum = (nelements + 1) / 2 * nsize;
		upbound0 = 6 * (nelements - 1) * (nelements - 1);
		idxforsum = new int[nsize2 + 2][nsize];
		fcons = new boolean[nelements];

		// Initialise the matrix elements
		if (isConstrained) {
			int idxpin = prow * nsize + pcol;
			for (ii = 0; ii < 3; ii++) {
				for (jj = 0; jj < 3; jj++) {
					fcons[idxpin + ii * nsize + jj] = true;
				}
			}
			int c1 = 1, c2 = 10;
			for (ii = 0; ii < nelements; ii++) {
				if (fcons[ii]) {
					matrix[ii] = c1;
					c1++;
				} else {
					matrix[ii] = c2;
					c2++;
				}
			}
		} else {
			for (ii = 0; ii < nelements; ii++)
				matrix[ii] = ii + 1;
		}
		populateIdxforsum();
		// calculate the sums
		calcSums();
		calcDistance();
	}

	public boolean isIndexConstrained(int idx) {
		return fcons[idx];
	}

	/**
	 * Calculate the summations of every rows, columns and two diagonals.
	 */
	private void calcSums() {
		int ii, jj;
		int[] indices;

		for (ii = 0; ii < nsize2 + 2; ii++) {
			indices = idxforsum[ii];
			idxs[ii] = ii;
			sums[ii] = 0;
			for (jj = 0; jj < nsize; jj++) {
				sums[ii] += matrix[indices[jj]];
			}
		}
	}

	private void calcDistance() {
		distance = 0;
		for (int val : sums) {
			distance += (val - goalsum) * (val - goalsum);
		}
	}

	/**
	 * Find out which sums that are affected for a given element.
	 */
	private int updateIdxSumChange(int idx) {
		int q, m;
		int nchanges = 2;

		q = idx / nsize;
		m = idx % nsize;
		idxSumChange[0] = q;
		idxSumChange[1] = nsize + m;

		// diagonal 1
		if (q == m) {
			idxSumChange[2] = nsize2;
			nchanges++;
		}
		// diagonal 2
		if (q + m == nsize - 1) {
			idxSumChange[3] = nsize2 + 1;
			nchanges++;
		}
		return nchanges;
	}

	/**
	 * Update the matrix by swapping two elements and update the sums, distance.
	 * 
	 * @param idx1
	 * @param idx2
	 */
	public void update(int idx1, int idx2) {
		int ii;
		int dev;
		int diff;

		matrixOld = matrix.clone();
		distanceOld = distance;
		sumsOld = sums.clone();

		diff = matrix[idx1] - matrix[idx2];
		for (ii = 0; ii < updateIdxSumChange(idx1); ii++) {
			dev = sums[idxSumChange[ii]] - goalsum;
			distance -= dev * dev;
			sums[idxSumChange[ii]] -= diff;
			dev -= diff;
			distance += dev * dev;
		}
		for (ii = 0; ii < updateIdxSumChange(idx2); ii++) {
			dev = sums[idxSumChange[ii]] - goalsum;
			distance -= dev * dev;
			sums[idxSumChange[ii]] += diff;
			dev += diff;
			distance += dev * dev;
		}
		matrix[idx1] -= diff;
		matrix[idx2] += diff;
	}

	public boolean verifyUpdateSimple() {
		if (distance < distanceOld)
			return true;
		else
			return false;
	}
	
	public void updatePairedSwap(int idx1, int idxg1, int idx2, int idxg2) {
		int ii;
		int dev;
		int diff;

		matrixOld = matrix.clone();
		distanceOld = distance;
		sumsOld = sums.clone();

		diff = matrix[idx1] - matrix[idxg1];
		for (ii = 0; ii < updateIdxSumChange(idx1); ii++) {
			dev = sums[idxSumChange[ii]] - goalsum;
			distance -= dev * dev;
			sums[idxSumChange[ii]] -= diff;
			dev -= diff;
			distance += dev * dev;
		}
		for (ii = 0; ii < updateIdxSumChange(idxg1); ii++) {
			dev = sums[idxSumChange[ii]] - goalsum;
			distance -= dev * dev;
			sums[idxSumChange[ii]] += diff;
			dev += diff;
			distance += dev * dev;
		}
		matrix[idx1] -= diff;
		matrix[idxg1] += diff;
		
		diff = matrix[idx2] - matrix[idxg2];
		for (ii = 0; ii < updateIdxSumChange(idx2); ii++) {
			dev = sums[idxSumChange[ii]] - goalsum;
			distance -= dev * dev;
			sums[idxSumChange[ii]] -= diff;
			dev -= diff;
			distance += dev * dev;
		}
		for (ii = 0; ii < updateIdxSumChange(idxg2); ii++) {
			dev = sums[idxSumChange[ii]] - goalsum;
			distance -= dev * dev;
			sums[idxSumChange[ii]] += diff;
			dev += diff;
			distance += dev * dev;
		}
		matrix[idx2] -= diff;
		matrix[idxg2] += diff;
		
	}
	
	
	public boolean verifyUpdatePairedSwap() {
		if (distance < distanceOld)
			return true;
		else
			return false;
	}

	public void revertUpdate() {
		int ii;
		for (ii = 0; ii < nelements; ii++) {
			matrix[ii] = matrixOld[ii];
		}
		distance = distanceOld;
		for (ii = 0; ii < sums.length; ii++) {
			sums[ii] = sumsOld[ii];
		}
	}

	public Integer[] getIdxSortSums() {
		Integer[] idxsort = idxs.clone();
		Arrays.sort(idxsort, new Comparator<Integer>() {
			@Override
			public int compare(final Integer i1, final Integer i2) {
				return sums[i1] - sums[i2];
			}
		});

		return idxsort;
	}

	/**
	 * Count the number of unique values of the sums array except zeros.
	 * 
	 * @param idxsort
	 * @return
	 */
	public int countNuniqueSumsExceptZero(Integer[] idxsort) {
		int ii, count, thesum, exceptZero;

		thesum = sums[idxsort[0]];
		count = 1;
		exceptZero = 0;
		for (ii = 1; ii < sums.length; ii++) {
			if (sums[ii] == 0)
				exceptZero = 1;
			if (thesum == sums[ii]) {
				continue;
			} else {
				thesum = sums[ii];
				count++;
			}
		}
		count -= exceptZero;
		return count;
	}

	public void populateIdxforsum() {
		int ii, jj, idxpin;

		// Sum for every rows
		for (ii = 0; ii < nsize; ii++) {
			idxpin = ii * nsize;
			for (jj = 0; jj < nsize; jj++) {
				idxforsum[ii][jj] = idxpin + jj;
			}
		}

		// Sum for every columns
		for (ii = 0; ii < nsize; ii++) {
			for (jj = 0; jj < nsize; jj++) {
				idxforsum[nsize + ii][jj] = ii + jj * nsize;
			}
		}

		// Sum for diagonals
		for (ii = 0; ii < nsize; ii++) {
			idxforsum[nsize2][ii] = ii * nsize + ii;
			idxforsum[nsize2 + 1][ii] = ii * nsize + nsize - ii - 1;
		}
	}

	public void print() {
		int counter = 0;

		for (int number : matrix) {
			System.out.print("" + number + " ");
			counter++;
			if (counter == nsize) {
				System.out.println();
				counter = 0;
			}
		}
	}

	public void printsums() {
		for (int number : sums)
			System.out.print(number + " ");
		System.out.println();
	}

	public int[] getMatrix() {
		return matrix;
	}

	public int getIndexForElement(int value) {
		int ii;
		if (value <= 0 || value > nelements)
			return -1;
		for (ii = 0; ii < nelements; ii++) {
			if (value == matrix[ii])
				return ii;
		}
		return -1;
	}

	public long getDistance() {
		return distance;
	}

	public int[] getSums() {
		return sums;
	}

	public int[] getIndicesOfSingleSum(int idxsum) {
		return idxforsum[idxsum];
	}

	public Integer[] getSortedIndexOfSingleSumElements(int idxsum) {
		Integer[] idxforsum_sort = new Integer[nsize];
		for (int ii = 0; ii < nsize; ii++) {
			idxforsum_sort[ii] = idxforsum[idxsum][ii];
		}
		Arrays.sort(idxforsum_sort, new Comparator<Integer>() {
			@Override
			public int compare(final Integer i1, final Integer i2) {
				return matrix[i1] - matrix[i2];
			}
		});
		return idxforsum_sort;
	}

	public long getUpbound0() {
		return upbound0;
	}

	public boolean[] getFcons() {
		return fcons;
	}

	public int getGoalsum() {
		return goalsum;
	}

}
