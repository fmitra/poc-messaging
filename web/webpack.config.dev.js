const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const local = {
  sources: path.resolve(__dirname, 'src/'),
};

module.exports = {
  mode: 'development',
  context: local.sources,
  entry: './index.js',

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
    extensions: ['.js', '.jsx'],
    alias: {
      '@messaging': local.sources,
    }
  },

  module: {
    rules: [
      {
        test: /\.(?:js|jsx)$/,
        loader: 'babel-loader',
        exclude: /node_modules/,

        options: {
          presets: [
            '@babel/react',
            '@babel/env'
          ],
          plugins: [
            [
              '@babel/plugin-transform-react-jsx', {
                'pragma': 'h',
                'pragmaFrag': 'Fragment'
              }
            ]
          ]
        }
      }
    ]
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: 'index.ejs'
    })
  ]
};
