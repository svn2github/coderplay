/**
 * 
 */
package src;

import java.util.Arrays;

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
	private int[] sums;
	private boolean[] fcons; // the constraint flag matrix

	private int[] idxSumChange = new int[4];

	public MSMatrix(int n, boolean isConstrained, int prow, int pcol) {

		int ii, jj;
		nsize = n;
		nsize2 = nsize + nsize;
		nelements = nsize * nsize;
		matrix = new int[nelements];
		sums = new int[nsize2 + 2];
		goalsum = (nelements + 1)/2*nsize;

		if (isConstrained) {
			fcons = new boolean[nelements];
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

		calcSums();
	}

	/**
	 * Calculate the summations of every rows, columns and two diagonals.
	 */
	private void calcSums() {
		int ii, jj;
		int sum;
		int idxpin;

		// Sum for every rows
		for (ii = 0; ii < nsize; ii++) {
			sum = 0;
			idxpin = ii * nsize;
			for (jj = 0; jj < nsize; jj++) {
				sum += matrix[idxpin + jj];
			}
			sums[ii] = sum;
		}

		// Sum for every columns
		for (ii = 0; ii < nsize; ii++) {
			sum = 0;
			for (jj = 0; jj < nsize; jj++) {
				sum += matrix[ii + jj * nsize];
			}
			sums[nsize + ii] = sum;
		}

		// Sum for diagonals
		for (ii = 0; ii < nsize; ii++) {
			sum = 0;
			sums[nsize2] += matrix[ii * nsize + ii];
			sums[nsize2 + 1] += matrix[ii * nsize + nsize - ii - 1];
		}
	}

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
	 * Update the sums for a swap of two numbers.
	 * 
	 * @param idx1
	 * @param idx2
	 */
	public void updateSums(int idx1, int idx2) {
		int ii;
		int diff = matrix[idx1] - matrix[idx2];
		for (ii=0;ii<updateIdxSumChange(idx1);ii++) {
			sums[idxSumChange[ii]] -= diff;
		}
		for (ii=0;ii<updateIdxSumChange(idx2);ii++) {
			sums[idxSumChange[ii]] += diff;
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

}
