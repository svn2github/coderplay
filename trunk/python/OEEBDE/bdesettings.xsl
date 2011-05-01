<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template match="/">

		<HTML xmlns="http://www.w3.org/1999/xhtml">
			<head>
				<title>OEE BDE File Processing Configurations</title>
				<style type="text/css">
					body {
					margin-left: 0px;
					margin-top: 0px;
					margin-right: 0px;
					margin-bottom: 0px;
					}
					.style1 {
					font-family: Arial,
					Helvetica, sans-serif;
					font-weight: bold;
					}
					.style2 {font-size: 24px}
					.style3 {color: #FFFFFF}
				</style>
			</head>

			<BODY bgcolor="#BDCBDE">
				<table width="100%" border="0" cellpadding="0" cellspacing="0">
					<tr bgcolor="#003A7D">
						<td width="83%" valign="middle">
							<div align="left" class="style1 style2">
								<div align="center" class="style3">OEE BDE File Processing
									Configurations
								</div>
							</div>
						</td>
						<td width="17%" valign="middle">
							<img src="http://www.au.heidelberg.com/www/img/logo.gif" />
						</td>
					</tr>
				</table>
				<div>

					<xsl:for-each select="BdeSettings/Header/Client">
						<P>
							<B>Client: </B>
							<xsl:value-of select="Name" />
						</P>
					</xsl:for-each>
					<xsl:for-each select="BdeSettings/Header/Operator">
						<P>
							<B>Operator: </B>
							<xsl:value-of select="Name"></xsl:value-of>
						</P>
					</xsl:for-each>

					<h4>Sumup Configuration</h4>
					<table border="1">
						<tr color="#BDCBDE">
							<th>
								<font color="#003A7D">Name</font>
							</th>
							<th>
								<font color="#003A7D">Start Rule</font>
							</th>
							<th>
								<font color="#003A7D">Terminate Rule</font>
							</th>
							<th>
								<font color="#003A7D">End Rule</font>
							</th>
						</tr>
						<xsl:for-each select="BdeSettings/Sumups/Categories/Category">
							<tr>
								<td>
									<xsl:value-of select="@Name" />
								</td>
								<td>
									<xsl:value-of select="StartRule/@Name" />
								</td>
								<td>
									<xsl:value-of select="TerminateRule/@Name" />
								</td>
								<td>
									<xsl:value-of select="EndRule/@Name" />
								</td>
							</tr>
						</xsl:for-each>
					</table>

					<br></br>
					<h4>Reporting Configuration</h4>
					<table border="1">
						<tr bgcolor="#BDCBDE">
							<th>
								<font color="#003A7D">Name</font>
							</th>
							<th>
								<font color="#003A7D">Rules</font>
							</th>
						</tr>
						<xsl:for-each select="BdeSettings/Reporting/Categories/Category">
							<tr>
								<td>
									<xsl:value-of select="@Name"></xsl:value-of>
								</td>
								<td>
									<xsl:for-each select="Rules/Rule">
										<xsl:value-of select="@Name" />
										<xsl:text>, </xsl:text>
									</xsl:for-each>
								</td>
							</tr>
						</xsl:for-each>
					</table>
				</div>
			</BODY>
		</HTML>
	</xsl:template>



</xsl:stylesheet>
