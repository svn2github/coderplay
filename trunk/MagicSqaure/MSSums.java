/**
 * 
 */
package src;

import java.util.Arrays;
import java.util.Comparator;

/**
 * @author ywang
 * 
 */
public class MSSums {
	private Integer[] sums;
	private Integer[] idxs;
	private int nsize;
	private int nsize2;

	public MSSums(int[] matrix, int nsize) {
		this.nsize = nsize;
		this.nsize2 = nsize + nsize;
		int sumsize = nsize2 + 2;
		
		sums = new Integer[sumsize];
		idxs = new Integer[sumsize];

		calculate(matrix, nsize);
	}
	
	public void calculate(int[] matrix, int nsize) {
		int ii, jj;
		int thissum;
		int idxpin;
		// Sum for every rows
		for (ii = 0; ii < nsize; ii++) {
			thissum = 0;
			idxpin = ii * nsize;
			for (jj = 0; jj < nsize; jj++) {
				thissum += matrix[idxpin + jj];
			}
			sums[ii] = thissum;
			idxs[ii] = ii;
		}
		// Sum for every columns
		for (ii = 0; ii < nsize; ii++) {
			thissum = 0;
			for (jj = 0; jj < nsize; jj++) {
				thissum += matrix[ii + jj * nsize];
			}
			sums[nsize + ii] = thissum;
			idxs[nsize + ii] = nsize + ii;
		}
		// Sum for diagonals
		for (ii = 0; ii < nsize; ii++) {
			thissum = 0;
			sums[nsize2] = matrix[ii * nsize + ii];
			sums[nsize2 + 1] = matrix[ii * nsize + nsize - ii - 1];
			idxs[nsize2] = nsize2;
			idxs[nsize2 + 1] = nsize2 + 1;

		}
	}
	
	public void update() {
		
	}
	
	public Integer[] sort() {
		
		Integer [] idxsort = idxs.clone();
		
		Arrays.sort(idxsort, new Comparator<Integer>() {
			@Override public int compare(final Integer i1, final Integer i2) {
				return sums[i1] - sums[i2];
			}
		});
		
		return idxsort;
		
	}
	
	
	
	
	
}
