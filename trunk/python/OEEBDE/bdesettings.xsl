<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template match="/">

		<html xmlns="http://www.w3.org/1999/xhtml">
			<head>
				<title>OEE BDE File Processing Configurations</title>
				<script type="text/javascript">
					function changeClientName()
					{
						alert("I am an alert box!");
					}
				</script>
				<style type="text/css">
					body {
					background-color: #003A7D;
					margin: 0px;
					padding: 7px;
					font-family: Arial,
					Helvetica, sans-serif;
					font-weight:
					bold;
					}

					.nobordertable {
					margin: 0px;
					border: 0px;
					padding: 0px;
					border-collapse:collapse;
					border-spacing: 0px;
					}

					.titlestyle {
					text-align: center;
					width: 83%;
					valign:
					middle;
					font-size:
					24px;
					font-weight: bold;
					color: #FFFFFF;
					}

				</style>
			</head>

			<body>

				<table class="nobordertable" style="width:100%;background-color:#BDCBDE">
					<tr style="background-color:#003A7D;">
						<td class="titlestyle" style="padding-bottom:7px;">
							OEE BDE File Processing
							Configurations
						</td>
						<td>
							<img src="http://www.au.heidelberg.com/www/img/logo.gif" />
						</td>
					</tr>



					<tr>
						<td>
							<xsl:for-each select="BdeSettings/Header/Client">
								<p>
									<b>Client: </b>
									<xsl:value-of select="Name" />
									<button type="button" onClick="changeClientName()">...
									</button>
								</p>
							</xsl:for-each>
							<xsl:for-each select="BdeSettings/Header/Operator">
								<p>
									<b>Operator: </b>
									<xsl:value-of select="Name"></xsl:value-of>
								</p>
							</xsl:for-each>

							<table border="1">
								<caption>
									<b>Sumup Configuration</b>
								</caption>
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
										<th>
											<xsl:value-of select="@Name" />
										</th>
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
							<table border="1">
								<caption>
									<b>Reporting Configuration</b>
								</caption>
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
										<th>
											<xsl:value-of select="@Name"></xsl:value-of>
										</th>
										<td>
											<xsl:for-each select="Rules/Rule">
												<xsl:value-of select="@Name" />
												<xsl:text>, </xsl:text>
											</xsl:for-each>
										</td>
									</tr>
								</xsl:for-each>
							</table>

						</td>
					</tr>
				</table>

			</body>
		</html>
	</xsl:template>



</xsl:stylesheet>
