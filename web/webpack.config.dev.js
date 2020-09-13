const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const local = {
  sources: path.resolve(__dirname, 'src/'),
};

module.exports = {
  mode: 'development',
  context: local.sources,
  entry: './index.tsx',

  output: {
    path: local.sources,
    publicPath: '/',
    filename: 'app.js'
  },

  devtool: 'cheap-module-eval-source-map',
  target: 'web',

  devServer: {
    contentBase: 'src',
    compress: true,
    port: 4000,
    disableHostCheck: true
  },

  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
    alias: {
      '@messaging': local.sources,
    }
  },

  module: {
    rules: [
      {
        test: /\.(?:ts|tsx)$/,
        loader: 'ts-loader',
        exclude: /node_modules/
      }
    ]
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: 'index.ejs'
    })
  ]
};
